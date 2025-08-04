from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from pydantic import BaseModel, Field

from core.config import settings
from core.models import (
    Scenario, FeedbackAnalysis, ScoreDetail,
    MedicalAccuracyDetail, ClarityDetail, EmpathyDetail, CompletenessDetail
)
from services.storage_service import StorageService
from prompts.analysis_system_prompts import get_analysis_system_prompt


class ScenarioWeights(BaseModel):
    """Model for scenario-specific weights"""
    medical_accuracy: float = Field(ge=0, le=1, description="Weight for medical accuracy (0-1)")
    communication_clarity: float = Field(ge=0, le=1, description="Weight for communication clarity (0-1)")
    empathy_tone: float = Field(ge=0, le=1, description="Weight for empathy and tone (0-1)")
    completeness: float = Field(ge=0, le=1, description="Weight for completeness (0-1)")
    rationale: str = Field(description="Explanation for why these weights are appropriate for this scenario")


class CombinedCommunicationAnalysis(BaseModel):
    """Combined analysis for clarity, empathy, and completeness in a single API call"""
    clarity: ClarityDetail = Field(description="Communication clarity analysis")
    empathy: EmpathyDetail = Field(description="Empathy and tone analysis")
    completeness: CompletenessDetail = Field(description="Completeness analysis")

class AnalysisPipelineService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            temperature=0.1
        )
        
        self.storage_service = StorageService()
        
        # Cache for scenario weights to avoid regenerating
        self._weights_cache: Dict[str, ScenarioWeights] = {}

    def _generate_scenario_weights(self, scenario: Scenario) -> ScenarioWeights:
        """Generate appropriate weights for this scenario type"""
        
        # Check cache first
        cache_key = f"{scenario.medical_area}_{scenario.difficulty}_{scenario.patient_type}"
        if cache_key in self._weights_cache:
            print(f"Using cached weights for scenario type: {cache_key}")
            return self._weights_cache[cache_key]
        
        print(f"Generating new weights for scenario type: {cache_key}")
        
        weight_prompt = ChatPromptTemplate.from_messages([
            ("system", get_analysis_system_prompt("weight_generation")),
            ("user", """
            Scenario: {title}
            Description: {description}
            Context: {context}
            Medical Area: {medical_area}
            Difficulty: {difficulty}
            Patient Type: {patient_type}
            Key Points: {key_points}
            
            Generate appropriate weights for the four analysis categories that sum to 1.0.
            """)
        ])
        
        chain = weight_prompt | self.llm.with_structured_output(ScenarioWeights)
        
        weights = chain.invoke({
            "title": scenario.title,
            "description": scenario.description,
            "context": scenario.context,
            "medical_area": scenario.medical_area,
            "difficulty": scenario.difficulty,
            "patient_type": scenario.patient_type,
            "key_points": ", ".join(scenario.key_points)
        })
        
        # Ensure weights sum to 1.0 (normalize if needed)
        total = weights.medical_accuracy + weights.communication_clarity + weights.empathy_tone + weights.completeness
        if abs(total - 1.0) > 0.01:  # Allow small floating point variance
            weights.medical_accuracy /= total
            weights.communication_clarity /= total
            weights.empathy_tone /= total
            weights.completeness /= total
            print(f"Normalized weights to sum to 1.0 (was {total})")
        
        # Cache the weights
        self._weights_cache[cache_key] = weights        
        return weights

    def _create_specialist_chain(self, system_prompt: str, output_schema: Any, user_prompt_template: str):
        """A factory function to create a single analysis chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt_template)
        ])
        return prompt | self.llm.with_structured_output(output_schema)

    def _aggregate_results_with_weights(self, parallel_output: Dict[str, Any], attempt_id: str, 
                                      past_feedback_exists: bool, weights: ScenarioWeights) -> FeedbackAnalysis:
        """Aggregate all analysis results into final feedback using weighted scoring"""
        medical = parallel_output['medical']
        combined_comm = parallel_output['combined_communication']
        passthrough = parallel_output['passthrough']
        clarity = combined_comm.clarity
        empathy = combined_comm.empathy
        completeness = combined_comm.completeness

        # Calculate weighted overall score
        weighted_score = (
            medical.score * weights.medical_accuracy +
            clarity.score * weights.communication_clarity +
            empathy.score * weights.empathy_tone +
            completeness.score * weights.completeness
        )
        overall_score = round(weighted_score, 2)

        # Generate feedback mentioning the weighting rationale
        general_feedback = f"Overall Score: {overall_score}/10 (weighted scoring applied). "
        
        # Identify top performing categories
        category_scores = [
            ("medical accuracy", medical.score, weights.medical_accuracy),
            ("clarity", clarity.score, weights.communication_clarity),
            ("empathy", empathy.score, weights.empathy_tone),
            ("completeness", completeness.score, weights.completeness)
        ]
        
        strengths = [name for name, score, weight in category_scores if score > 8]
        if strengths:
            general_feedback += f"Your key strengths were in {', '.join(strengths)}. "

        # Add weight context
        highest_weight_category = max(category_scores, key=lambda x: x[2])
        general_feedback += f"For this scenario type, {highest_weight_category[0]} was weighted most heavily ({highest_weight_category[2]:.1%}) because {weights.rationale.lower()}. "

        if past_feedback_exists:
            general_feedback += "Considering your past performance, it's great to see you're applying feedback effectively. Keep up the great work. "
        else:
            general_feedback += "This is a great starting point. "

        general_feedback += "Continue practicing to refine your skills further."

        return FeedbackAnalysis(
            attempt_id=attempt_id,
            scenario_id=passthrough['scenario_id'],
            medical_accuracy=ScoreDetail(
                score=medical.score,
                explanation=medical.explanation,
                strengths=medical.strengths,
                improvements=medical.improvements,
                examples=medical.examples if hasattr(medical, 'examples') else []
            ),
            communication_clarity=ScoreDetail(**clarity.dict()),
            empathy_tone=ScoreDetail(**empathy.dict()),
            completeness=ScoreDetail(**completeness.dict()),
            overall_score=overall_score,
            general_feedback=general_feedback
        )

    def get_rag_context(self, user_id: str):
        """Get relevant context from past feedback for this user"""
        past_feedback_list = self.storage_service.get_recent_feedback_for_user(user_id)
        rag_context = ""
        if past_feedback_list:
            feedback_points = "\n".join(f"- {fb}" for fb in past_feedback_list)
            rag_context = (
                "**IMPORTANT CONTEXT**: This user has received the following feedback on previous attempts. "
                "Pay close attention to see if they have improved in these areas.\n"
                "---\n"
                f"{feedback_points}\n"
                "---\n"
            )
        return rag_context
    
    def analyze_response(self, attempt_id: str, scenario: Scenario, user_response: str, user_id: str) -> FeedbackAnalysis:
        """Main analysis method with cost-optimized weighted scoring system"""
        
        # Step 1: Generate/retrieve weights for this scenario type
        weights = self._generate_scenario_weights(scenario)
        
        # Get RAG context for analyses
        rag_context = self.get_rag_context(user_id)
        base_user_prompt = """
            Scenario Context: {context}
            Key Points to Cover: {key_points}
            ---
            Healthcare Professional's Response:
            "{user_response}"
            ---
            Please provide your analysis based ONLY on your specific role.
            """

        enhanced_user_prompt = rag_context + base_user_prompt

        parallel_chains = RunnableParallel(
            medical=self._create_specialist_chain(
                system_prompt=get_analysis_system_prompt("enhanced_medical"),
                output_schema=MedicalAccuracyDetail,
                user_prompt_template=base_user_prompt
            ),
            combined_communication=self._create_specialist_chain(
                system_prompt=get_analysis_system_prompt("combined_communication"),
                output_schema=CombinedCommunicationAnalysis,
                user_prompt_template=enhanced_user_prompt
            ),
            passthrough=RunnablePassthrough()
        )

        full_pipeline = parallel_chains | (
            lambda x: self._aggregate_results_with_weights(x, attempt_id, rag_context != "", weights))

        final_feedback = full_pipeline.invoke({
            "context": scenario.context,
            "key_points": ", ".join(scenario.key_points),
            "user_response": user_response,
            "scenario_id": scenario.id
        })
        
        return final_feedback