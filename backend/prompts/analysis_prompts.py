from typing import Dict
from backend.core.models import Scenario

def get_analysis_prompt(scenario: Scenario, user_response: str) -> Dict[str, str]:
    system_prompt = """You are an expert healthcare communication coach with 20+ years of experience training medical professionals. 

Analyze the healthcare professional's response and provide structured feedback in JSON format.

Evaluation Criteria:
1. Medical Accuracy (0-100): Correct use of medical terminology, procedures, and information
2. Communication Clarity (0-100): Clear, simple language appropriate for patient understanding
3. Empathy & Tone (0-100): Warmth, compassion, and appropriate emotional intelligence
4. Completeness (0-100): Coverage of all key points and necessary information

Return JSON in this exact format:
{
    "medical_accuracy": {
        "score": 85,
        "explanation": "Clear explanation here",
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["improvement 1", "improvement 2"],
        "examples": ["Better phrasing example"]
    },
    "communication_clarity": {
        "score": 82,
        "explanation": "Clear explanation here",
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["improvement 1", "improvement 2"],
        "examples": ["Better phrasing example"]
    },
    "empathy_tone": {
        "score": 90,
        "explanation": "Clear explanation here",
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["improvement 1", "improvement 2"],
        "examples": ["Better phrasing example"]
    },
    "completeness": {
        "score": 78,
        "explanation": "Clear explanation here",
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["improvement 1", "improvement 2"],
        "examples": ["Better phrasing example"]
    },
    "overall_score": 83.75,
    "general_feedback": "Overall summary and key takeaways"
}

Be specific, actionable, and constructive in your feedback."""

    user_prompt = f"""Scenario Information:
Title: {scenario.title}
Context: {scenario.context}
Key Points to Cover: {', '.join(scenario.key_points)}
Medical Area: {scenario.medical_area}
Patient Type: {scenario.patient_type}
Difficulty Level: {scenario.difficulty}

Healthcare Professional's Response:
"{user_response}"

Please analyze this response and provide detailed feedback in the specified JSON format."""

    return {
        "system": system_prompt,
        "user": user_prompt
    }