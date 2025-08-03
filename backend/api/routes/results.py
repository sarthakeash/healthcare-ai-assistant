from typing import List
from fastapi import APIRouter
from backend.core.models import FeedbackAnalysis, PracticeAttempt
from backend.services.storage_service import StorageService

router = APIRouter()
storage_service = StorageService()

@router.get("/feedback", response_model=List[FeedbackAnalysis])
async def get_all_feedback(limit: int = 50):
    """Get all feedback results"""
    return storage_service.get_all_feedback(limit)

@router.get("/attempts", response_model=List[PracticeAttempt])
async def get_all_attempts(limit: int = 50):
    """Get all practice attempts"""
    return storage_service.get_attempts(limit)

@router.get("/feedback/{attempt_id}", response_model=FeedbackAnalysis)
async def get_feedback_by_attempt(attempt_id: str):
    """Get feedback for a specific attempt"""
    feedback = storage_service.get_feedback_by_attempt_id(attempt_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback