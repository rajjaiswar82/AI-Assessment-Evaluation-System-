"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from models import DifficultyLevel, AssessmentStatus


# ============= Assessment Schemas =============

class AssessmentCreate(BaseModel):
    """Schema for creating a new assessment"""
    candidate_id: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=1, max_length=100)


class AssessmentResponse(BaseModel):
    """Schema for assessment response"""
    id: int
    candidate_id: str
    domain: str
    status: AssessmentStatus
    total_questions: int
    total_score: float
    max_possible_score: float
    percentage: float
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============= Question Schemas =============

class QuestionCreate(BaseModel):
    """Schema for creating a question"""
    assessment_id: int
    question_text: str = Field(..., min_length=10)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    domain: str
    max_score: float = Field(default=10.0, ge=0, le=100)
    expected_keywords: Optional[str] = None


class QuestionResponse(BaseModel):
    """Schema for question response"""
    id: int
    assessment_id: int
    question_text: str
    difficulty: DifficultyLevel
    domain: str
    max_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Answer Schemas =============

class AnswerSubmit(BaseModel):
    """Schema for submitting an answer"""
    assessment_id: int
    question_id: int
    candidate_id: str = Field(..., min_length=1, max_length=100)
    answer_text: str = Field(..., min_length=1)


class AnswerResponse(BaseModel):
    """Schema for answer response"""
    id: int
    assessment_id: int
    question_id: int
    candidate_id: str
    answer_text: str
    submitted_at: datetime
    
    class Config:
        from_attributes = True


# ============= Score Schemas =============

class MetricScores(BaseModel):
    """Schema for individual metric scores"""
    correctness_score: float = Field(..., ge=0, le=10)
    depth_score: float = Field(..., ge=0, le=10)
    clarity_score: float = Field(..., ge=0, le=10)


class NegativeMarking(BaseModel):
    """Schema for negative marking details"""
    negative_marks: float
    negative_reason: Optional[str]


class ScoreResponse(BaseModel):
    """Schema for score response"""
    id: int
    answer_id: int
    correctness_score: float
    depth_score: float
    clarity_score: float
    weighted_score: float
    negative_marks: float
    negative_reason: Optional[str]
    final_score: float
    evaluation_feedback: Optional[str]
    evaluated_at: datetime
    
    class Config:
        from_attributes = True


class EvaluationRequest(BaseModel):
    """Schema for evaluation request"""
    answer_id: int
    use_ai: bool = Field(default=False, description="Use real AI (OpenAI) for evaluation")


class EvaluationResponse(BaseModel):
    """Schema for complete evaluation response"""
    answer_id: int
    question_text: str
    answer_text: str
    metric_scores: MetricScores
    weighted_score: float
    negative_marking: NegativeMarking
    final_score: float
    max_score: float
    percentage: float
    evaluation_feedback: str
    evaluated_at: datetime


# ============= Candidate Score History =============

class CandidateScoreHistory(BaseModel):
    """Schema for candidate score history"""
    assessment_id: int
    domain: str
    question_id: int
    question_text: str
    answer_text: str
    final_score: float
    max_score: float
    percentage: float
    submitted_at: datetime
    evaluated_at: Optional[datetime]


class CandidateReport(BaseModel):
    """Schema for candidate overall report"""
    candidate_id: str
    total_assessments: int
    total_questions_answered: int
    average_score: float
    highest_score: float
    lowest_score: float
    assessments: List[AssessmentResponse]
    score_history: List[CandidateScoreHistory]
