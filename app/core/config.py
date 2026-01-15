"""
Application configuration and settings.
"""

from pydantic import BaseModel
from typing import Optional


class Settings(BaseModel):
    """Application settings."""

    # App settings
    APP_NAME: str = "Job Recommendation API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # NLP Settings
    SKILLS_EXTRACTION_MODEL: str = "kaliani/flair-ner-skill"
    MAX_SKILLS_EXTRACTED: int = 15

    # Job recommendation settings
    DEFAULT_TOP_N_RECOMMENDATIONS: int = 5
    MIN_MATCH_SCORE: float = 0.0  # Return all matches

    # Scraper settings
    SCRAPER_TIMEOUT: int = 30
    ENABLE_JOB_SCRAPING: bool = True


# Create settings instance with defaults
settings = Settings()

