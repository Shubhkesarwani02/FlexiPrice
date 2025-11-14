from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    PROJECT_NAME: str = "FlexiPrice"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENV: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    # ML Configuration
    ML_MODEL_PATH: str = "./ml_models"
    DISCOUNT_CALCULATION_SCHEDULE: str = "0 */6 * * *"  # Every 6 hours
    
    # Discount Rules
    MIN_DISCOUNT_PCT: float = 5.0
    MAX_DISCOUNT_PCT: float = 80.0
    EXPIRY_THRESHOLD_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
