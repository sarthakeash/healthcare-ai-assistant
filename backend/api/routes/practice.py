from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from core.models import PracticeAttempt, FeedbackAnalysis
# Import the new pipeline service
from services.advanced_analysis_service import AnalysisPipelineService
from services.scenario_service import ScenarioService
from services.storage_service import StorageService

router = APIRouter()
# Instantiate the new pipeline service
analysis_service = AnalysisPipelineService()
scenario_service = ScenarioService()
storage_service = StorageService()

class PracticeRequest(BaseModel):
    scenario_id: str
    user_response: str
    user_id: str = "default_user"

@router.post("/submit", response_model=FeedbackAnalysis)
async def submit_practice(request: PracticeRequest):
    """Submit a practice attempt and receive AI feedback from the pipeline."""
    try:
        attempt = PracticeAttempt(
            scenario_id=request.scenario_id,
            user_response=request.user_response,
            user_id=request.user_id
        )
        scenario = scenario_service.get_scenario(attempt.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Use the new AnalysisPipelineService
        feedback = analysis_service.analyze_response(
            attempt_id=attempt.id,
            scenario=scenario,
            user_response=attempt.user_response,
            user_id=attempt.user_id # user_id is passed but not used in this version
        )
        
        storage_service.save_attempt(attempt)
        storage_service.save_feedback(feedback)
        
        return feedback
        
    except Exception as e:
        print(f"An error occurred in submit_practice: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")