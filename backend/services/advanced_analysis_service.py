from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from core.config import settings
from core.models import (
    Scenario, FeedbackAnalysis, ScoreDetail,
    MedicalAccuracyDetail, ClarityDetail, EmpathyDetail, CompletenessDetail
)

class AnalysisPipelineService:
    """
    Implements a multi-stage "Chain of Thought" analysis pipeline.
    
    This service runs four specialized analysis chains in parallel and then
    aggregates their results into a final, comprehensive feedback object.
    """
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            temperature=0.1
        )

        # Each chain focuses on ONE specific task.
        accuracy_chain = self._create_specialist_chain(
            system_prompt="You are a senior medical doctor. Analyze the medical accuracy of the following response. Ignore tone, empathy, and clarity. Focus ONLY on medical facts and terminology.",
            output_schema=MedicalAccuracyDetail
        )
        clarity_chain = self._create_specialist_chain(
            system_prompt="You are a patient communication coach. Analyze the clarity of the following response. Ignore medical accuracy. Focus ONLY on how easy the language would be for a nervous patient to understand. Avoid jargon.",
            output_schema=ClarityDetail
        )
        empathy_chain = self._create_specialist_chain(
            system_prompt="You are an expert in patient psychology. Analyze the empathy and tone of the following response. Ignore medical details. Focus ONLY on whether the tone is reassuring, compassionate, and professional.",
            output_schema=EmpathyDetail
        )
        completeness_chain = self._create_specialist_chain(
            system_prompt="You are a meticulous clinical auditor. Analyze if the response covers all necessary points. Compare the response against the 'Key Points to Cover'. Focus ONLY on completeness.",
            output_schema=CompletenessDetail
        )

        self.parallel_chains = RunnableParallel(
            medical=accuracy_chain,
            clarity=clarity_chain,
            empathy=empathy_chain,
            completeness=completeness_chain,
            passthrough=RunnablePassthrough()
        )

    def _create_specialist_chain(self, system_prompt: str, output_schema: Any):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", """
            Scenario Context: {context}
            Key Points to Cover: {key_points}
            ---
            Healthcare Professional's Response:
            "{user_response}"
            ---
            Please provide your analysis based ONLY on your specific role.
            """)
        ])
        return prompt | self.llm.with_structured_output(output_schema)

    def _aggregate_results(self, parallel_output: Dict[str, Any], attempt_id: str) -> FeedbackAnalysis:
        """
        Combines the parallel outputs into the final FeedbackAnalysis object.
        This step is done in reliable Python code, not by the LLM.
        """
        medical = parallel_output['medical']
        clarity = parallel_output['clarity']
        empathy = parallel_output['empathy']
        completeness = parallel_output['completeness']
        passthrough = parallel_output['passthrough']
        overall_score = round((medical.score + clarity.score + empathy.score + completeness.score) / 4, 2)
        
        general_feedback = f"Excellent work. You scored {overall_score} overall. Your key strength was in {max(['Medical Accuracy', 'Clarity', 'Empathy', 'Completeness'], key=lambda k: getattr(parallel_output[k.lower().split()[0]], 'score'))}. The main area for improvement is {min(['Medical Accuracy', 'Clarity', 'Empathy', 'Completeness'], key=lambda k: getattr(parallel_output[k.lower().split()[0]], 'score'))}."

        return FeedbackAnalysis(
            attempt_id=attempt_id,
            scenario_id=passthrough['scenario_id'],
            medical_accuracy=ScoreDetail(**medical.dict()),
            communication_clarity=ScoreDetail(**clarity.dict()),
            empathy_tone=ScoreDetail(**empathy.dict()),
            completeness=ScoreDetail(**completeness.dict()),
            overall_score=overall_score,
            general_feedback=general_feedback
        )

    def analyze_response(self, attempt_id: str, scenario: Scenario, user_response: str, user_id: str) -> FeedbackAnalysis:
        """
        Runs the full parallel pipeline and aggregates the results.
        """
        full_pipeline = self.parallel_chains | (lambda x: self._aggregate_results(x, attempt_id))
        
        final_feedback = full_pipeline.invoke({
            "context": scenario.context,
            "key_points": ", ".join(scenario.key_points),
            "user_response": user_response,
            "scenario_id": scenario.id 
        })

        return final_feedback