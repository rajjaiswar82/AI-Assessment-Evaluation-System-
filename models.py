"""
SQLAlchemy Database Models for AI Assessment System
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class DifficultyLevel(str, enum.Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AssessmentStatus(str, enum.Enum):
    """Assessment status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EVALUATED = "evaluated"


class Assessment(Base):
    """Assessment table - stores assessment sessions"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String(100), nullable=False, index=True)
    domain = Column(String(100), nullable=False)
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.IN_PROGRESS)
    total_questions = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    max_possible_score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="assessment", cascade="all, delete-orphan")


class Question(Base):
    """Question table - stores questions for assessments"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    domain = Column(String(100), nullable=False)
    max_score = Column(Float, default=10.0)
    expected_keywords = Column(Text, nullable=True)  # JSON string of keywords
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    """Answer table - stores candidate answers"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    candidate_id = Column(String(100), nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    score = relationship("Score", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class Score(Base):
    """Score table - stores evaluation scores"""
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False, unique=True)
    
    # Metric scores (0-10 scale)
    correctness_score = Column(Float, default=0.0)
    depth_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    
    # Weighted score
    weighted_score = Column(Float, default=0.0)
    
    # Negative marking
    negative_marks = Column(Float, default=0.0)
    negative_reason = Column(Text, nullable=True)
    
    # Final score
    final_score = Column(Float, default=0.0)
    
    # AI evaluation details
    evaluation_feedback = Column(Text, nullable=True)
    
    # Timestamps
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    answer = relationship("Answer", back_populates="score")


class EvaluationLog(Base):
    """Evaluation log table - stores evaluation history and monitoring"""
    __tablename__ = "evaluation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, nullable=False, index=True)
    candidate_id = Column(String(100), nullable=False, index=True)
    question_id = Column(Integer, nullable=False)
    answer_id = Column(Integer, nullable=False)
    
    # Evaluation metadata
    evaluation_method = Column(String(50), default="ai_scoring")  # ai_scoring, manual, hybrid
    processing_time_ms = Column(Integer, nullable=True)
    
    # Scores snapshot
    final_score = Column(Float, default=0.0)
    negative_marks = Column(Float, default=0.0)
    
    # Timestamp
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
