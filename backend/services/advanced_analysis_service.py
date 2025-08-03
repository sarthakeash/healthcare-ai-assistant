from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from core.config import settings
from core.models import (
    Scenario, FeedbackAnalysis, ScoreDetail,
    MedicalAccuracyDetail, ClarityDetail, EmpathyDetail, CompletenessDetail
)
from services.storage_service import StorageService
from prompts.analysis_system_prompts import get_analysis_system_prompt


class AnalysisPipelineService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            temperature=0.1
        )

        self.storage_service = StorageService()

    def _create_specialist_chain(self, system_prompt: str, output_schema: Any, user_prompt_template: str):
        """A factory function to create a single analysis chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt_template)
        ])
        return prompt | self.llm.with_structured_output(output_schema)

    def _aggregate_results(self, parallel_output: Dict[str, Any], attempt_id: str, past_feedback_exists:bool) -> FeedbackAnalysis:
        medical = parallel_output['medical']
        clarity = parallel_output['clarity']
        empathy = parallel_output['empathy']
        completeness = parallel_output['completeness']
        passthrough = parallel_output['passthrough']

        overall_score = round(
            (medical.score + clarity.score + empathy.score + completeness.score) / 4, 2)

        general_feedback = f"Overall Score: {overall_score}/10. "
        strengths = []
        if medical.score > 8:
            strengths.append("medical accuracy")
        if clarity.score > 8:
            strengths.append("clarity")
        if empathy.score > 8:
            strengths.append("empathy")
        if completeness.score > 8:
            strengths.append("completeness")
        if strengths:
            general_feedback += f"Your key strengths were in {', '.join(strengths)}. "

        if past_feedback_exists:
            general_feedback += "Considering your past performance, it's great to see you're applying feedback effectively. Keep up the great work. "
        else:
            general_feedback += "This is a great starting point. "

        general_feedback += "Continue practicing to refine your skills further."

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

    def get_rag_context(self, user_id: str):
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
        rag_context=self.get_rag_context(user_id)
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

        accuracy_chain = self._create_specialist_chain(
            system_prompt=get_analysis_system_prompt("medical"),
            output_schema=MedicalAccuracyDetail,
            user_prompt_template=base_user_prompt
        )
        clarity_chain = self._create_specialist_chain(
            system_prompt=get_analysis_system_prompt("clarity"),
            output_schema=ClarityDetail,
            user_prompt_template=base_user_prompt
        )
        empathy_chain = self._create_specialist_chain(
            system_prompt=get_analysis_system_prompt("empathy"),
            output_schema=EmpathyDetail,
            user_prompt_template=enhanced_user_prompt
        )
        completeness_chain = self._create_specialist_chain(
            system_prompt=get_analysis_system_prompt("completeness"),
            output_schema=CompletenessDetail,
            user_prompt_template=enhanced_user_prompt
        )

        parallel_chains = RunnableParallel(
            medical=accuracy_chain,
            clarity=clarity_chain,
            empathy=empathy_chain,
            completeness=completeness_chain,
            passthrough=RunnablePassthrough()
        )

        full_pipeline = parallel_chains | (
            lambda x: self._aggregate_results(x, attempt_id, rag_context !=""))

        final_feedback = full_pipeline.invoke({
            "context": scenario.context,
            "key_points": ", ".join(scenario.key_points),
            "user_response": user_response,
            "scenario_id": scenario.id
        })

        return final_feedback
