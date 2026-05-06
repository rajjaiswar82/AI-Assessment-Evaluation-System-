"""
Business Logic Services for AI Assessment System
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime

import models
import schemas
from evaluation_engine import AIEvaluationEngine, NegativeMarkingEngine
from score_calculator import ScoreCalculator


class AssessmentService:
    """Service for managing assessments"""
    
    @staticmethod
    def create_assessment(db: Session, assessment_data: schemas.AssessmentCreate) -> models.Assessment:
        """Create a new assessment"""
        assessment = models.Assessment(
            candidate_id=assessment_data.candidate_id,
            domain=assessment_data.domain,
            status=models.AssessmentStatus.IN_PROGRESS
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment
    
    @staticmethod
    def get_assessment(db: Session, assessment_id: int) -> Optional[models.Assessment]:
        """Get assessment by ID"""
        return db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
    
    @staticmethod
    def get_candidate_assessments(db: Session, candidate_id: str) -> List[models.Assessment]:
        """Get all assessments for a candidate"""
        return db.query(models.Assessment).filter(
            models.Assessment.candidate_id == candidate_id
        ).order_by(models.Assessment.created_at.desc()).all()
    
    @staticmethod
    def complete_assessment(db: Session, assessment_id: int) -> models.Assessment:
        """Mark assessment as completed and calculate total score"""
        assessment = db.query(models.Assessment).filter(models.Assessment.id == assessment_id).first()
        if not assessment:
            return None
        
        # Get all scores for this assessment
        scores = db.query(models.Score).join(models.Answer).filter(
            models.Answer.assessment_id == assessment_id
        ).all()
        
        # Get all questions for this assessment
        questions = db.query(models.Question).filter(
            models.Question.assessment_id == assessment_id
        ).all()
        
        # Calculate totals
        final_scores = [score.final_score for score in scores]
        max_scores = [q.max_score for q in questions]
        
        calculator = ScoreCalculator()
        totals = calculator.calculate_assessment_total(final_scores, max_scores)
        
        # Update assessment
        assessment.status = models.AssessmentStatus.COMPLETED
        assessment.total_questions = len(questions)
        assessment.total_score = totals["total_score"]
        assessment.max_possible_score = totals["max_possible_score"]
        assessment.percentage = totals["percentage"]
        assessment.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(assessment)
        return assessment


class QuestionService:
    """Service for managing questions"""
    
    @staticmethod
    def create_question(db: Session, question_data: schemas.QuestionCreate) -> models.Question:
        """Create a new question"""
        question = models.Question(
            assessment_id=question_data.assessment_id,
            question_text=question_data.question_text,
            difficulty=question_data.difficulty,
            domain=question_data.domain,
            max_score=question_data.max_score,
            expected_keywords=question_data.expected_keywords
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    
    @staticmethod
    def get_question(db: Session, question_id: int) -> Optional[models.Question]:
        """Get question by ID"""
        return db.query(models.Question).filter(models.Question.id == question_id).first()
    
    @staticmethod
    def get_assessment_questions(db: Session, assessment_id: int) -> List[models.Question]:
        """Get all questions for an assessment"""
        return db.query(models.Question).filter(
            models.Question.assessment_id == assessment_id
        ).all()


class AnswerService:
    """Service for managing answers"""
    
    @staticmethod
    def submit_answer(db: Session, answer_data: schemas.AnswerSubmit) -> models.Answer:
        """Submit a candidate answer"""
        answer = models.Answer(
            assessment_id=answer_data.assessment_id,
            question_id=answer_data.question_id,
            candidate_id=answer_data.candidate_id,
            answer_text=answer_data.answer_text
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer
    
    @staticmethod
    def get_answer(db: Session, answer_id: int) -> Optional[models.Answer]:
        """Get answer by ID"""
        return db.query(models.Answer).filter(models.Answer.id == answer_id).first()
    
    @staticmethod
    def get_candidate_answers(db: Session, candidate_id: str) -> List[models.Answer]:
        """Get all answers for a candidate"""
        return db.query(models.Answer).filter(
            models.Answer.candidate_id == candidate_id
        ).order_by(models.Answer.submitted_at.desc()).all()


class EvaluationService:
    """Service for evaluating answers and calculating scores"""
    
    def __init__(self):
        self.ai_engine = AIEvaluationEngine()
        self.negative_marking = NegativeMarkingEngine()
        self.calculator = ScoreCalculator()
    
    def evaluate_answer(
        self,
        db: Session,
        answer_id: int,
        use_real_ai: bool = False
    ) -> Dict:
        """
        Evaluate an answer and store the score
        
        Args:
            db: Database session
            answer_id: ID of the answer to evaluate
            use_real_ai: Whether to use real AI (OpenAI) - not implemented in this version
        
        Returns:
            Dictionary with evaluation results
        """
        # Get answer and question
        answer = db.query(models.Answer).filter(models.Answer.id == answer_id).first()
        if not answer:
            raise ValueError(f"Answer with ID {answer_id} not found")
        
        question = db.query(models.Question).filter(models.Question.id == answer.question_id).first()
        if not question:
            raise ValueError(f"Question with ID {answer.question_id} not found")
        
        # Evaluate using AI engine
        eval_result = self.ai_engine.evaluate_answer(
            question=question.question_text,
            answer=answer.answer_text,
            expected_keywords=question.expected_keywords,
            max_score=question.max_score
        )
        
        # Apply negative marking
        negative_marks, negative_reason = self.negative_marking.apply_negative_marking(
            answer=answer.answer_text,
            correctness_score=eval_result["correctness_score"],
            depth_score=eval_result["depth_score"],
            clarity_score=eval_result["clarity_score"]
        )
        
        # Calculate final score
        final_score_result = self.calculator.calculate_final_score(
            weighted_score=eval_result["weighted_score"],
            negative_marks=negative_marks,
            max_score=question.max_score
        )
        
        # Store score in database
        score = models.Score(
            answer_id=answer_id,
            correctness_score=eval_result["correctness_score"],
            depth_score=eval_result["depth_score"],
            clarity_score=eval_result["clarity_score"],
            weighted_score=eval_result["weighted_score"],
            negative_marks=negative_marks,
            negative_reason=negative_reason,
            final_score=final_score_result["final_score"],
            evaluation_feedback=eval_result["evaluation_feedback"]
        )
        db.add(score)
        
        # Log evaluation
        log = models.EvaluationLog(
            assessment_id=answer.assessment_id,
            candidate_id=answer.candidate_id,
            question_id=answer.question_id,
            answer_id=answer_id,
            evaluation_method="ai_scoring",
            processing_time_ms=eval_result["processing_time_ms"],
            final_score=final_score_result["final_score"],
            negative_marks=negative_marks
        )
        db.add(log)
        
        db.commit()
        db.refresh(score)
        
        # Return complete evaluation result
        return {
            "answer_id": answer_id,
            "question_text": question.question_text,
            "answer_text": answer.answer_text,
            "metric_scores": {
                "correctness_score": eval_result["correctness_score"],
                "depth_score": eval_result["depth_score"],
                "clarity_score": eval_result["clarity_score"]
            },
            "weighted_score": eval_result["weighted_score"],
            "negative_marking": {
                "negative_marks": negative_marks,
                "negative_reason": negative_reason
            },
            "final_score": final_score_result["final_score"],
            "max_score": question.max_score,
            "percentage": final_score_result["percentage"],
            "evaluation_feedback": eval_result["evaluation_feedback"],
            "evaluated_at": datetime.utcnow()
        }
    
    def get_score(self, db: Session, answer_id: int) -> Optional[models.Score]:
        """Get score for an answer"""
        return db.query(models.Score).filter(models.Score.answer_id == answer_id).first()


class ReportService:
    """Service for generating reports"""
    
    @staticmethod
    def get_candidate_report(db: Session, candidate_id: str) -> Dict:
        """Generate comprehensive report for a candidate"""
        # Get all assessments
        assessments = db.query(models.Assessment).filter(
            models.Assessment.candidate_id == candidate_id
        ).order_by(models.Assessment.created_at.desc()).all()
        
        # Get all answers with scores
        answers = db.query(models.Answer, models.Score, models.Question).join(
            models.Score, models.Answer.id == models.Score.answer_id
        ).join(
            models.Question, models.Answer.question_id == models.Question.id
        ).filter(
            models.Answer.candidate_id == candidate_id
        ).order_by(models.Answer.submitted_at.desc()).all()
        
        # Calculate statistics
        scores = [score.final_score for _, score, _ in answers]
        
        score_history = []
        for answer, score, question in answers:
            percentage = (score.final_score / question.max_score * 100) if question.max_score > 0 else 0
            score_history.append({
                "assessment_id": answer.assessment_id,
                "domain": question.domain,
                "question_id": question.id,
                "question_text": question.question_text,
                "answer_text": answer.answer_text,
                "final_score": score.final_score,
                "max_score": question.max_score,
                "percentage": round(percentage, 2),
                "submitted_at": answer.submitted_at,
                "evaluated_at": score.evaluated_at
            })
        
        return {
            "candidate_id": candidate_id,
            "total_assessments": len(assessments),
            "total_questions_answered": len(answers),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "highest_score": round(max(scores), 2) if scores else 0.0,
            "lowest_score": round(min(scores), 2) if scores else 0.0,
            "assessments": assessments,
            "score_history": score_history
        }
