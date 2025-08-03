from enum import EnumType
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from core.models import PracticeAttempt, FeedbackAnalysis,InputType
from fastapi import UploadFile, File
from services.transcription_service import TranscriptionService
# Import the new pipeline service
from services.advanced_analysis_service import AnalysisPipelineService
from services.scenario_service import ScenarioService
from services.storage_service import StorageService

router = APIRouter()
# Instantiate the new pipeline service
analysis_service = AnalysisPipelineService()
scenario_service = ScenarioService()
storage_service = StorageService()
transcription_service = TranscriptionService()


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

@router.post("/submit_voice", response_model=FeedbackAnalysis)
async def submit_practice_voice(
    scenario_id: str = File(...),
    user_id: str = File(...),
    audio_file: UploadFile = File(...)
):
    """
    Submit a voice-based practice attempt, transcribe it, and receive AI feedback.
    """
    try:
        # 1. Transcribe the audio file to get the user's response text
        user_response_text = await transcription_service.transcribe_audio(audio_file)

        if not user_response_text:
            raise HTTPException(status_code=400, detail="Audio could not be transcribed or was empty.")

        # 2. Now, proceed with the existing logic using the transcribed text
        attempt = PracticeAttempt(
            scenario_id=scenario_id,
            user_response=user_response_text,
            user_id=user_id,
            input_type=InputType.VOICE # Set the input type to voice
        )
        
        scenario = scenario_service.get_scenario(attempt.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # 3. Reuse your entire advanced analysis pipeline
        feedback = analysis_service.analyze_response(
            attempt_id=attempt.id,
            scenario=scenario,
            user_response=attempt.user_response,
            user_id=attempt.user_id
        )
        
        # 4. Save the results as usual
        storage_service.save_attempt(attempt)
        storage_service.save_feedback(feedback)
        
        return feedback
        
    except Exception as e:
        print(f"An error occurred in submit_practice_voice: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")