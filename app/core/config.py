"""
Application configuration and settings.
"""

from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


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

    # Supabase settings
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "resumes")
    USE_SUPABASE_STORAGE: bool = os.getenv("USE_SUPABASE_STORAGE", "True").lower() == "true"

    # CORS settings - Client URLs
    CLIENT_URL1: Optional[str] = os.getenv("CLIENT_URL1")
    CLIENT_URL2: Optional[str] = os.getenv("CLIENT_URL2")
    CLIENT_URL3: Optional[str] = os.getenv("CLIENT_URL3")

    class Config:
        arbitrary_types_allowed = True


# Create settings instance with defaults
settings = Settings()

