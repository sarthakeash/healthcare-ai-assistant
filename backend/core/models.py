from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class InputType(str, Enum):
    TEXT = "text"
    VOICE = "voice"

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
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    scenario_id: str
    user_response: str
    input_type: InputType = InputType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)
    
class ScoreDetail(BaseModel):
    score: float = Field(ge=0, le=100)
    explanation: str
    strengths: List[str]
    improvements: List[str]
    examples: Optional[List[str]] = []

class FeedbackAnalysis(BaseModel):
    attempt_id: str
    scenario_id: str
    medical_accuracy: ScoreDetail
    communication_clarity: ScoreDetail
    empathy_tone: ScoreDetail
    completeness: ScoreDetail
    overall_score: float
    general_feedback: str
    timestamp: datetime = Field(default_factory=datetime.now)

# SQLAlchemy Models
class PracticeAttemptDB(Base):
    __tablename__ = "practice_attempts"
    
    id = Column(String, primary_key=True)
    scenario_id = Column(String, nullable=False)
    user_response = Column(Text, nullable=False)
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