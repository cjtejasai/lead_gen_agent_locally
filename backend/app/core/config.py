from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "Lyncsea"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database - PostgreSQL
    DATABASE_URL: str = "postgresql://ayka:ayka_secure_password_123@localhost:5432/ayka"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # AssemblyAI
    ASSEMBLYAI_API_KEY: str = "f26801f0f12c40fd8e1548ceb8babb79"

    # Speech-to-Text Provider
    # Options: "local_whisper" (uses local Whisper+Pyannote) or "assemblyai" (cloud API)
    STT_PROVIDER: str = "assemblyai"  # Default to local for dev
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    ENABLE_DIARIZATION: bool = True  # Speaker diarization

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = "ayka-recordings"
    AWS_REGION: str = "us-east-1"

    # Google Calendar API
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "1233"

    # Sentry
    SENTRY_DSN: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 500000000  # 500MB
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a", ".flac"]
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".mov", ".avi"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Don't raise error if .env file is missing
        env_file_encoding = 'utf-8'
        extra = 'allow'


# Create settings instance
try:
    settings = Settings()
except Exception as e:
    # If .env is missing or has issues, use defaults
    logger.warning(f"Could not load .env file: {e}")
    logger.warning("Using default configuration. Please create backend/.env file for production.")
    settings = Settings(_env_file=None)
