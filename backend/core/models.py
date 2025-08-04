from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, conint
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ScenarioWeights(BaseModel):
    """Model for scenario-specific weights"""
    medical_accuracy: float = Field(ge=0, le=1, description="Weight for medical accuracy (0-1)")
    communication_clarity: float = Field(ge=0, le=1, description="Weight for communication clarity (0-1)")
    empathy_tone: float = Field(ge=0, le=1, description="Weight for empathy and tone (0-1)")
    completeness: float = Field(ge=0, le=1, description="Weight for completeness (0-1)")
    rationale: str = Field(description="Explanation for why these weights are appropriate for this scenario")


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class InputType(str, Enum):
    TEXT = "text"
    VOICE = "voice"


class MedicalAccuracyDetail(BaseModel):
    score: conint(ge=0, le=10) = Field(...,
                                       description="Score for medical accuracy (0-10)")
    explanation: str = Field(...,
                             description="Explanation for the medical accuracy score")
    strengths: List[str] = Field(...,
                                 description="Strengths in medical accuracy")
    improvements: List[str] = Field(...,
                                    description="Areas for improvement in medical accuracy")


class ClarityDetail(BaseModel):
    score: conint(ge=0, le=10) = Field(...,
                                       description="Score for communication clarity (0-10)")
    explanation: str = Field(...,
                             description="Explanation for the communication clarity score")
    strengths: List[str] = Field(...,
                                 description="Strengths in communication clarity")
    improvements: List[str] = Field(
        ..., description="Areas for improvement in communication clarity")


class EmpathyDetail(BaseModel):
    score: conint(ge=0, le=10) = Field(...,     
                                       description="Score for empathy and tone (0-10)")
    explanation: str = Field(...,
                             description="Explanation for the empathy and tone score")
    strengths: List[str] = Field(...,
                                 description="Strengths in empathy and tone")
    improvements: List[str] = Field(...,
                                    description="Areas for improvement in empathy and tone")


class CompletenessDetail(BaseModel):
    score: conint(ge=0, le=10) = Field(...,
                                       description="Score for completeness (0-10)")
    explanation: str = Field(...,
                             description="Explanation for the completeness score")
    strengths: List[str] = Field(..., description="Strengths in completeness")
    improvements: List[str] = Field(...,
                                    description="Areas for improvement in completeness")


class CombinedCommunicationAnalysis(BaseModel):
    """Combined analysis for clarity, empathy, and completeness in a single API call"""
    clarity: ClarityDetail = Field(description="Communication clarity analysis")
    empathy: EmpathyDetail = Field(description="Empathy and tone analysis")
    completeness: CompletenessDetail = Field(description="Completeness analysis")


class Scenario(BaseModel):
    id: str
    title: str
    description: str
    context: str
    difficulty: DifficultyLevel
    medical_area: str
    patient_type: str
    key_points: List[str]


class PracticeAttempt(BaseModel):
    id: str = Field(
        default_factory=lambda: f"attempt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    scenario_id: str
    user_response: str
    user_id: str = "default_user"  # Added for personalization
    input_type: InputType = InputType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)


class ScoreDetail(BaseModel):
    """A model for a single feedback criterion."""
    score: conint(ge=0, le=10) = Field(...,
                                       description="The score from 0 to 10 for this criterion.")  # type: ignore
    explanation: str = Field(
        ..., description="A detailed explanation for the score, justifying the rating.")
    strengths: List[str] = Field(...,
                                 description="Specific examples of what the user did well.")
    improvements: List[str] = Field(
        ..., description="Specific, actionable suggestions for improvement.")
    examples: Optional[List[str]] = Field(
        default=[], description="Concrete examples of better phrasing or alternative approaches.")


class FeedbackAnalysis(BaseModel):
    """The complete, structured feedback for a user's practice attempt."""
    attempt_id: str
    scenario_id: str
    medical_accuracy: ScoreDetail
    communication_clarity: ScoreDetail
    empathy_tone: ScoreDetail
    completeness: ScoreDetail
    overall_score: float = Field(...,
                                 description="The weighted average of all scores.")
    general_feedback: str = Field(
        ..., description="A high-level summary and the most important takeaways for the user.")
    timestamp: datetime = Field(default_factory=datetime.now)


class PracticeAttemptDB(Base):
    __tablename__ = "practice_attempts"
    id = Column(String, primary_key=True)
    scenario_id = Column(String, nullable=False)
    user_response = Column(Text, nullable=False)
    user_id = Column(String, default="default_user")  # Add user_id to DB model
    input_type = Column(SQLEnum(InputType), default=InputType.TEXT)
    timestamp = Column(DateTime, default=datetime.now)


class FeedbackAnalysisDB(Base):
    __tablename__ = "feedback_analyses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    attempt_id = Column(String, nullable=False)
    scenario_id = Column(String, nullable=False)

    medical_accuracy_score = Column(Float)
    medical_accuracy_explanation = Column(Text)
    medical_accuracy_strengths = Column(Text)
    medical_accuracy_improvements = Column(Text)
    medical_accuracy_examples = Column(Text)

    communication_clarity_score = Column(Float)
    communication_clarity_explanation = Column(Text)
    communication_clarity_strengths = Column(Text)
    communication_clarity_improvements = Column(Text)
    communication_clarity_examples = Column(Text)

    empathy_tone_score = Column(Float)
    empathy_tone_explanation = Column(Text)
    empathy_tone_strengths = Column(Text)
    empathy_tone_improvements = Column(Text)
    empathy_tone_examples = Column(Text)

    completeness_score = Column(Float)
    completeness_explanation = Column(Text)
    completeness_strengths = Column(Text)
    completeness_improvements = Column(Text)
    completeness_examples = Column(Text)

    overall_score = Column(Float)
    general_feedback = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
