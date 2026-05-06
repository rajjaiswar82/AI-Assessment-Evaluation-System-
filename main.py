"""
FastAPI Main Application
AI Assessment Evaluation System
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

import models
import schemas
import services
from database import engine, get_db, init_db
from config import get_settings
from database import engine, get_db, init_db
from config import get_settings

settings = get_settings()

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-based assessment evaluation system with scoring and negative marking"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
assessment_service = services.AssessmentService()
question_service = services.QuestionService()
answer_service = services.AnswerService()
evaluation_service = services.EvaluationService()
report_service = services.ReportService()


# ============= Health Check =============

@app.get("/", tags=["Health"])
def root():
    """Serve the main UI"""
    return FileResponse("static/index.html")


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# ============= Assessment Endpoints =============

@app.post("/assessments", response_model=schemas.AssessmentResponse, tags=["Assessments"])
def create_assessment(
    assessment: schemas.AssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new assessment session"""
    return assessment_service.create_assessment(db, assessment)


@app.get("/assessments/{assessment_id}", response_model=schemas.AssessmentResponse, tags=["Assessments"])
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Get assessment by ID"""
    assessment = assessment_service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@app.get("/assessments/candidate/{candidate_id}", response_model=List[schemas.AssessmentResponse], tags=["Assessments"])
def get_candidate_assessments(candidate_id: str, db: Session = Depends(get_db)):
    """Get all assessments for a candidate"""
    return assessment_service.get_candidate_assessments(db, candidate_id)


@app.post("/assessments/{assessment_id}/complete", response_model=schemas.AssessmentResponse, tags=["Assessments"])
def complete_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Complete an assessment and calculate final scores"""
    assessment = assessment_service.complete_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


# ============= Question Endpoints =============

@app.post("/questions", response_model=schemas.QuestionResponse, tags=["Questions"])
def create_question(
    question: schemas.QuestionCreate,
    db: Session = Depends(get_db)
):
    """Create a new question for an assessment"""
    return question_service.create_question(db, question)


@app.get("/questions/{question_id}", response_model=schemas.QuestionResponse, tags=["Questions"])
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Get question by ID"""
    question = question_service.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.get("/assessments/{assessment_id}/questions", response_model=List[schemas.QuestionResponse], tags=["Questions"])
def get_assessment_questions(assessment_id: int, db: Session = Depends(get_db)):
    """Get all questions for an assessment"""
    return question_service.get_assessment_questions(db, assessment_id)


# ============= Answer Endpoints =============

@app.post("/answers", response_model=schemas.AnswerResponse, tags=["Answers"])
def submit_answer(
    answer: schemas.AnswerSubmit,
    db: Session = Depends(get_db)
):
    """Submit a candidate answer"""
    return answer_service.submit_answer(db, answer)


@app.get("/answers/{answer_id}", response_model=schemas.AnswerResponse, tags=["Answers"])
def get_answer(answer_id: int, db: Session = Depends(get_db)):
    """Get answer by ID"""
    answer = answer_service.get_answer(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return answer


# ============= Evaluation Endpoints =============

@app.post("/evaluate/{answer_id}", response_model=schemas.EvaluationResponse, tags=["Evaluation"])
def evaluate_answer(
    answer_id: int,
    use_ai: bool = False,
    db: Session = Depends(get_db)
):
    """
    Evaluate an answer and return scores with negative marking
    
    - **answer_id**: ID of the answer to evaluate
    - **use_ai**: Use real AI (OpenAI) for evaluation (not implemented in this version)
    """
    try:
        result = evaluation_service.evaluate_answer(db, answer_id, use_ai)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/scores/{answer_id}", response_model=schemas.ScoreResponse, tags=["Evaluation"])
def get_score(answer_id: int, db: Session = Depends(get_db)):
    """Get score for an answer"""
    score = evaluation_service.get_score(db, answer_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score


# ============= Report Endpoints =============

@app.get("/reports/candidate/{candidate_id}", response_model=schemas.CandidateReport, tags=["Reports"])
def get_candidate_report(candidate_id: str, db: Session = Depends(get_db)):
    """Get comprehensive report for a candidate"""
    return report_service.get_candidate_report(db, candidate_id)


# ============= Quick Test Endpoint =============

@app.post("/quick-test", tags=["Testing"])
def quick_test(
    candidate_id: str,
    domain: str,
    question_text: str,
    answer_text: str,
    expected_keywords: str = None,
    db: Session = Depends(get_db)
):
    """
    Quick test endpoint for evaluating a single question-answer pair
    Creates assessment, question, answer, and evaluates in one call
    """
    # Create assessment
    assessment = assessment_service.create_assessment(
        db,
        schemas.AssessmentCreate(candidate_id=candidate_id, domain=domain)
    )
    
    # Create question
    question = question_service.create_question(
        db,
        schemas.QuestionCreate(
            assessment_id=assessment.id,
            question_text=question_text,
            difficulty=models.DifficultyLevel.MEDIUM,
            domain=domain,
            max_score=10.0,
            expected_keywords=expected_keywords
        )
    )
    
    # Submit answer
    answer = answer_service.submit_answer(
        db,
        schemas.AnswerSubmit(
            assessment_id=assessment.id,
            question_id=question.id,
            candidate_id=candidate_id,
            answer_text=answer_text
        )
    )
    
    # Evaluate
    evaluation = evaluation_service.evaluate_answer(db, answer.id)
    
    # Complete assessment
    completed_assessment = assessment_service.complete_assessment(db, assessment.id)
    
    return {
        "assessment": completed_assessment,
        "question": question,
        "answer": answer,
        "evaluation": evaluation
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Assessment Evaluation System...")
    print("📊 Server will be available at: http://localhost:8000")
    print("📚 API Documentation at: http://localhost:8000/docs")
    print("⏹️  Press CTRL+C to stop the server")
    print("-" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
