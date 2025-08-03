import json
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.core.models import (
    Base, PracticeAttempt, FeedbackAnalysis, PracticeAttemptDB, 
    FeedbackAnalysisDB, ScoreDetail
)

class StorageService:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def save_attempt(self, attempt: PracticeAttempt) -> bool:
        db = next(self.get_db())
        try:
            db_attempt = PracticeAttemptDB(
                id=attempt.id,
                scenario_id=attempt.scenario_id,
                user_response=attempt.user_response,
                input_type=attempt.input_type,
                timestamp=attempt.timestamp
            )
            db.add(db_attempt)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving attempt: {e}")
            return False
        finally:
            db.close()
    
    def save_feedback(self, feedback: FeedbackAnalysis) -> bool:
        db = next(self.get_db())
        try:
            db_feedback = FeedbackAnalysisDB(
                attempt_id=feedback.attempt_id,
                scenario_id=feedback.scenario_id,
                
                medical_accuracy_score=feedback.medical_accuracy.score,
                medical_accuracy_explanation=feedback.medical_accuracy.explanation,
                medical_accuracy_strengths=json.dumps(feedback.medical_accuracy.strengths),
                medical_accuracy_improvements=json.dumps(feedback.medical_accuracy.improvements),
                medical_accuracy_examples=json.dumps(feedback.medical_accuracy.examples or []),
                
                communication_clarity_score=feedback.communication_clarity.score,
                communication_clarity_explanation=feedback.communication_clarity.explanation,
                communication_clarity_strengths=json.dumps(feedback.communication_clarity.strengths),
                communication_clarity_improvements=json.dumps(feedback.communication_clarity.improvements),
                communication_clarity_examples=json.dumps(feedback.communication_clarity.examples or []),
                
                empathy_tone_score=feedback.empathy_tone.score,
                empathy_tone_explanation=feedback.empathy_tone.explanation,
                empathy_tone_strengths=json.dumps(feedback.empathy_tone.strengths),
                empathy_tone_improvements=json.dumps(feedback.empathy_tone.improvements),
                empathy_tone_examples=json.dumps(feedback.empathy_tone.examples or []),
                
                completeness_score=feedback.completeness.score,
                completeness_explanation=feedback.completeness.explanation,
                completeness_strengths=json.dumps(feedback.completeness.strengths),
                completeness_improvements=json.dumps(feedback.completeness.improvements),
                completeness_examples=json.dumps(feedback.completeness.examples or []),
                
                overall_score=feedback.overall_score,
                general_feedback=feedback.general_feedback,
                timestamp=feedback.timestamp
            )
            db.add(db_feedback)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving feedback: {e}")
            return False
        finally:
            db.close()
    
    def get_attempts(self, limit: int = 50) -> List[PracticeAttempt]:
        db = next(self.get_db())
        try:
            attempts = db.query(PracticeAttemptDB).order_by(PracticeAttemptDB.timestamp.desc()).limit(limit).all()
            return [
                PracticeAttempt(
                    id=attempt.id,
                    scenario_id=attempt.scenario_id,
                    user_response=attempt.user_response,
                    input_type=attempt.input_type,
                    timestamp=attempt.timestamp
                ) for attempt in attempts
            ]
        finally:
            db.close()
    
    def get_feedback_by_attempt_id(self, attempt_id: str) -> Optional[FeedbackAnalysis]:
        db = next(self.get_db())
        try:
            feedback = db.query(FeedbackAnalysisDB).filter(FeedbackAnalysisDB.attempt_id == attempt_id).first()
            if not feedback:
                return None
            
            return FeedbackAnalysis(
                attempt_id=feedback.attempt_id,
                scenario_id=feedback.scenario_id,
                medical_accuracy=ScoreDetail(
                    score=feedback.medical_accuracy_score,
                    explanation=feedback.medical_accuracy_explanation,
                    strengths=json.loads(feedback.medical_accuracy_strengths),
                    improvements=json.loads(feedback.medical_accuracy_improvements),
                    examples=json.loads(feedback.medical_accuracy_examples)
                ),
                communication_clarity=ScoreDetail(
                    score=feedback.communication_clarity_score,
                    explanation=feedback.communication_clarity_explanation,
                    strengths=json.loads(feedback.communication_clarity_strengths),
                    improvements=json.loads(feedback.communication_clarity_improvements),
                    examples=json.loads(feedback.communication_clarity_examples)
                ),
                empathy_tone=ScoreDetail(
                    score=feedback.empathy_tone_score,
                    explanation=feedback.empathy_tone_explanation,
                    strengths=json.loads(feedback.empathy_tone_strengths),
                    improvements=json.loads(feedback.empathy_tone_improvements),
                    examples=json.loads(feedback.empathy_tone_examples)
                ),
                completeness=ScoreDetail(
                    score=feedback.completeness_score,
                    explanation=feedback.completeness_explanation,
                    strengths=json.loads(feedback.completeness_strengths),
                    improvements=json.loads(feedback.completeness_improvements),
                    examples=json.loads(feedback.completeness_examples)
                ),
                overall_score=feedback.overall_score,
                general_feedback=feedback.general_feedback,
                timestamp=feedback.timestamp
            )
        finally:
            db.close()
    
    def get_all_feedback(self, limit: int = 50) -> List[FeedbackAnalysis]:
        db = next(self.get_db())
        try:
            feedbacks = db.query(FeedbackAnalysisDB).order_by(FeedbackAnalysisDB.timestamp.desc()).limit(limit).all()
            result = []
            for feedback in feedbacks:
                result.append(FeedbackAnalysis(
                    attempt_id=feedback.attempt_id,
                    scenario_id=feedback.scenario_id,
                    medical_accuracy=ScoreDetail(
                        score=feedback.medical_accuracy_score,
                        explanation=feedback.medical_accuracy_explanation,
                        strengths=json.loads(feedback.medical_accuracy_strengths),
                        improvements=json.loads(feedback.medical_accuracy_improvements),
                        examples=json.loads(feedback.medical_accuracy_examples)
                    ),
                    communication_clarity=ScoreDetail(
                        score=feedback.communication_clarity_score,
                        explanation=feedback.communication_clarity_explanation,
                        strengths=json.loads(feedback.communication_clarity_strengths),
                        improvements=json.loads(feedback.communication_clarity_improvements),
                        examples=json.loads(feedback.communication_clarity_examples)
                    ),
                    empathy_tone=ScoreDetail(
                        score=feedback.empathy_tone_score,
                        explanation=feedback.empathy_tone_explanation,
                        strengths=json.loads(feedback.empathy_tone_strengths),
                        improvements=json.loads(feedback.empathy_tone_improvements),
                        examples=json.loads(feedback.empathy_tone_examples)
                    ),
                    completeness=ScoreDetail(
                        score=feedback.completeness_score,
                        explanation=feedback.completeness_explanation,
                        strengths=json.loads(feedback.completeness_strengths),
                        improvements=json.loads(feedback.completeness_improvements),
                        examples=json.loads(feedback.completeness_examples)
                    ),
                    overall_score=feedback.overall_score,
                    general_feedback=feedback.general_feedback,
                    timestamp=feedback.timestamp
                ))
            return result
        finally:
            db.close()