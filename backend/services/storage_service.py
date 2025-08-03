# backend/services/storage_service.py
import json
import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.models import (
    Base, PracticeAttempt, FeedbackAnalysis, PracticeAttemptDB, 
    FeedbackAnalysisDB, ScoreDetail
)

class StorageService:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.results_dir = settings.results_dir
        self._ensure_results_dir()
    
    def _ensure_results_dir(self):
        """Ensure results directory exists with proper structure"""
        os.makedirs(self.results_dir, exist_ok=True)
        # Create subdirectories for better organization
        os.makedirs(os.path.join(self.results_dir, "attempts"), exist_ok=True)
        os.makedirs(os.path.join(self.results_dir, "feedback"), exist_ok=True)
        os.makedirs(os.path.join(self.results_dir, "daily_summaries"), exist_ok=True)
    
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def _save_to_json(self, data: dict, filepath: str):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def _get_daily_summary_path(self) -> str:
        """Get path for today's summary file"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.results_dir, "daily_summaries", f"summary_{today}.json")
    
    def _update_daily_summary(self, attempt_id: str, scenario_id: str, overall_score: float):
        """Update daily summary file"""
        summary_path = self._get_daily_summary_path()
        
        # Load existing summary or create new
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                summary = json.load(f)
        else:
            summary = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_attempts": 0,
                "average_score": 0,
                "attempts": [],
                "scenarios_practiced": {}
            }
        
        # Update summary
        summary["total_attempts"] += 1
        summary["attempts"].append({
            "attempt_id": attempt_id,
            "scenario_id": scenario_id,
            "score": overall_score,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update scenario count
        if scenario_id in summary["scenarios_practiced"]:
            summary["scenarios_practiced"][scenario_id] += 1
        else:
            summary["scenarios_practiced"][scenario_id] = 1
        
        # Recalculate average
        total_score = sum(attempt["score"] for attempt in summary["attempts"])
        summary["average_score"] = round(total_score / summary["total_attempts"], 2)
        
        # Save updated summary
        self._save_to_json(summary, summary_path)
    
    def save_attempt(self, attempt: PracticeAttempt) -> bool:
        """Save practice attempt to both database and JSON"""
        # Save to database
        db = next(self.get_db())
        try:
            db_attempt = PracticeAttemptDB(
                id=attempt.id,
                scenario_id=attempt.scenario_id,
                user_response=attempt.user_response,
                input_type=attempt.input_type,
                timestamp=attempt.timestamp,
                user_id=attempt.user_id
            )
            db.add(db_attempt)
            db.commit()
            
            # Save to JSON
            attempt_data = attempt.model_dump()
            json_path = os.path.join(
                self.results_dir, 
                "attempts", 
                f"{attempt.id}.json"
            )
            self._save_to_json(attempt_data, json_path)
            
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving attempt: {e}")
            return False
        finally:
            db.close()
    
    def save_feedback(self, feedback: FeedbackAnalysis) -> bool:
        """Save feedback to both database and JSON"""
        db = next(self.get_db())
        try:
            # Save to database
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
            
            # Save to JSON with full structure
            feedback_data = {
                "attempt_id": feedback.attempt_id,
                "scenario_id": feedback.scenario_id,
                "timestamp": feedback.timestamp.isoformat(),
                "overall_score": feedback.overall_score,
                "general_feedback": feedback.general_feedback,
                "detailed_scores": {
                    "medical_accuracy": {
                        "score": feedback.medical_accuracy.score,
                        "explanation": feedback.medical_accuracy.explanation,
                        "strengths": feedback.medical_accuracy.strengths,
                        "improvements": feedback.medical_accuracy.improvements,
                        "examples": feedback.medical_accuracy.examples or []
                    },
                    "communication_clarity": {
                        "score": feedback.communication_clarity.score,
                        "explanation": feedback.communication_clarity.explanation,
                        "strengths": feedback.communication_clarity.strengths,
                        "improvements": feedback.communication_clarity.improvements,
                        "examples": feedback.communication_clarity.examples or []
                    },
                    "empathy_tone": {
                        "score": feedback.empathy_tone.score,
                        "explanation": feedback.empathy_tone.explanation,
                        "strengths": feedback.empathy_tone.strengths,
                        "improvements": feedback.empathy_tone.improvements,
                        "examples": feedback.empathy_tone.examples or []
                    },
                    "completeness": {
                        "score": feedback.completeness.score,
                        "explanation": feedback.completeness.explanation,
                        "strengths": feedback.completeness.strengths,
                        "improvements": feedback.completeness.improvements,
                        "examples": feedback.completeness.examples or []
                    }
                }
            }
            
            # Save individual feedback JSON
            json_path = os.path.join(
                self.results_dir, 
                "feedback", 
                f"feedback_{feedback.attempt_id}.json"
            )
            self._save_to_json(feedback_data, json_path)
            
            # Update daily summary
            self._update_daily_summary(
                feedback.attempt_id, 
                feedback.scenario_id, 
                feedback.overall_score
            )
            
            # Also save a combined result file
            combined_path = os.path.join(
                self.results_dir,
                f"complete_result_{feedback.attempt_id}.json"
            )
            
            # Load the attempt data to create combined result
            attempt_path = os.path.join(
                self.results_dir, 
                "attempts", 
                f"{feedback.attempt_id}.json"
            )
            if os.path.exists(attempt_path):
                with open(attempt_path, 'r') as f:
                    attempt_data = json.load(f)
                
                combined_data = {
                    "attempt": attempt_data,
                    "feedback": feedback_data,
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }
                self._save_to_json(combined_data, combined_path)
            
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving feedback: {e}")
            return False
        finally:
            db.close()
    
    def get_attempts(self, limit: int = 50) -> List[PracticeAttempt]:
        """Get attempts from database"""
        db = next(self.get_db())
        try:
            attempts = db.query(PracticeAttemptDB).order_by(PracticeAttemptDB.timestamp.desc()).limit(limit).all()
            return [
                PracticeAttempt(
                    id=attempt.id,
                    scenario_id=attempt.scenario_id,
                    user_response=attempt.user_response,
                    input_type=attempt.input_type,
                    timestamp=attempt.timestamp,
                    user_id=attempt.user_id
                ) for attempt in attempts
            ]
        finally:
            db.close()
    
    def get_feedback_by_attempt_id(self, attempt_id: str) -> Optional[FeedbackAnalysis]:
        """Get feedback from database"""
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
        """Get all feedback from database"""
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

    def get_recent_feedback_for_user(self, user_id: str, limit: int = 3) -> List[str]:
        """Retrieves the general feedback from the most recent attempts for a given user."""
        db = next(self.get_db())
        try:
            recent_attempts = db.query(PracticeAttemptDB.id).filter(
                PracticeAttemptDB.user_id == user_id
            ).order_by(PracticeAttemptDB.timestamp.desc()).limit(limit).all()

            if not recent_attempts:
                return []
            
            attempt_ids = [attempt.id for attempt in recent_attempts]
            feedbacks = db.query(FeedbackAnalysisDB.general_feedback).filter(
                FeedbackAnalysisDB.attempt_id.in_(attempt_ids)
            ).all()

            return [fb.general_feedback for fb in feedbacks]
        except Exception as e:
            print(f"Error retrieving past feedback for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    def export_all_results_to_csv(self) -> str:
        """Export all results to a CSV file"""
        import csv
        from datetime import datetime
        
        db = next(self.get_db())
        try:
            # Get all feedback with attempts
            feedbacks = db.query(FeedbackAnalysisDB).all()
            
            # Create CSV file
            csv_path = os.path.join(
                self.results_dir,
                f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'attempt_id', 'scenario_id', 'timestamp', 'overall_score',
                    'medical_accuracy_score', 'communication_clarity_score',
                    'empathy_tone_score', 'completeness_score', 'user_id'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for feedback in feedbacks:
                    # Get the attempt to get user_id
                    attempt = db.query(PracticeAttemptDB).filter(
                        PracticeAttemptDB.id == feedback.attempt_id
                    ).first()
                    
                    writer.writerow({
                        'attempt_id': feedback.attempt_id,
                        'scenario_id': feedback.scenario_id,
                        'timestamp': feedback.timestamp,
                        'overall_score': feedback.overall_score,
                        'medical_accuracy_score': feedback.medical_accuracy_score,
                        'communication_clarity_score': feedback.communication_clarity_score,
                        'empathy_tone_score': feedback.empathy_tone_score,
                        'completeness_score': feedback.completeness_score,
                        'user_id': attempt.user_id if attempt else 'unknown'
                    })
            
            return csv_path
        finally:
            db.close()