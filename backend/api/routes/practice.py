from fastapi import APIRouter, HTTPException
from core.models import PracticeAttempt, FeedbackAnalysis
from services.llm_service import LLMService
from services.scenario_service import ScenarioService
from services.storage_service import StorageService

router = APIRouter()
llm_service = LLMService()
scenario_service = ScenarioService()
storage_service = StorageService()

@router.post("/submit", response_model=FeedbackAnalysis)
async def submit_practice(attempt: PracticeAttempt):
    """Submit a practice attempt and receive AI feedback"""
    try:
        # Get scenario
        scenario = scenario_service.get_scenario(attempt.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Analyze response
        analysis_result = llm_service.analyze_response(scenario, attempt.user_response)
        
        # Create feedback object
        feedback = FeedbackAnalysis(
            attempt_id=attempt.id,
            scenario_id=attempt.scenario_id,
            **analysis_result
        )
        
        # Store results
        storage_service.save_attempt(attempt)
        storage_service.save_feedback(feedback)
        
        return feedback
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))