"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "HalalScanner API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production"

    # Database
    DATABASE_URL: str = "postgresql://halaluser:halalpass123@localhost:5432/halalscanner"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://halaluser:halalpass123@localhost:5672/"

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "halalscanner-uploads"

    # Google Cloud Vision
    GOOGLE_CLOUD_VISION_API_KEY: Optional[str] = None

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@halalscanner.com"

    # ML Model
    ML_MODEL_PATH: str = "./models/ingredient_classifier.pt"

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # OCR
    TESSERACT_CMD: Optional[str] = None  # Path to tesseract executable
    OCR_CONFIDENCE_THRESHOLD: float = 0.6

    # Classification
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.7

    # Upload limits
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: set = {"image/jpeg", "image/png", "image/jpg"}

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
