"""
Configuration Management for AI Assessment System
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ai_assessment_db"
    
    # OpenAI (Optional)
    OPENAI_API_KEY: str = ""
    
    # Application
    APP_NAME: str = "AI Assessment Evaluation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Scoring Weights
    CORRECTNESS_WEIGHT: float = 0.5
    DEPTH_WEIGHT: float = 0.3
    CLARITY_WEIGHT: float = 0.2
    
    # Negative Marking Thresholds
    IRRELEVANT_PENALTY: float = -5.0
    INCORRECT_PENALTY: float = -3.0
    TOO_SHORT_PENALTY: float = -2.0
    HALLUCINATION_PENALTY: float = -4.0
    
    # Minimum answer length
    MIN_ANSWER_LENGTH: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
