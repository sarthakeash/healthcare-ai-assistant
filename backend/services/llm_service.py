import json
from typing import Dict, Any
from openai import OpenAI
from backend.core.config import settings
from backend.core.models import Scenario, FeedbackAnalysis, ScoreDetail
from backend.prompts.analysis_prompts import get_analysis_prompt

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def analyze_response(self, scenario: Scenario, user_response: str) -> Dict[str, Any]:
        """Analyze user response using OpenAI"""
        prompt = get_analysis_prompt(scenario, user_response)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert to our models
            return {
                "medical_accuracy": ScoreDetail(**result["medical_accuracy"]),
                "communication_clarity": ScoreDetail(**result["communication_clarity"]),
                "empathy_tone": ScoreDetail(**result["empathy_tone"]),
                "completeness": ScoreDetail(**result["completeness"]),
                "overall_score": result["overall_score"],
                "general_feedback": result["general_feedback"]
            }
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            # Return fallback feedback
            fallback_score = ScoreDetail(
                score=75.0,
                explanation="Unable to analyze due to technical error. Please try again.",
                strengths=["Response provided"],
                improvements=["Please try submitting again"],
                examples=[]
            )
            return {
                "medical_accuracy": fallback_score,
                "communication_clarity": fallback_score,
                "empathy_tone": fallback_score,
                "completeness": fallback_score,
                "overall_score": 75.0,
                "general_feedback": "Technical error occurred during analysis. Please try again."
            }