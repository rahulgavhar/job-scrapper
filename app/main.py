from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging
from app.api.routes import router
from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for job recommendations based on resume analysis",
    docs_url=None,
    redoc_url=None,
)

# Enable CORS
allowed_origins = ["https://applyrai.onrender.com", "https://hirely-ih11.onrender.com"]  # Default fallback

# Add client URLs if configured
if settings.CLIENT_URL1 or settings.CLIENT_URL2 or settings.CLIENT_URL3:
    allowed_origins = [
        url for url in [settings.CLIENT_URL1, settings.CLIENT_URL2, settings.CLIENT_URL3]
        if url is not None
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.on_event("startup")
def start_background_tasks():
    """Kick off background scraping via Celery without blocking startup."""
    try:
        from app.services.tasks import initial_linkedin_scrape

        initial_linkedin_scrape.delay()
        logger.info("Enqueued initial_linkedin_scrape Celery task")
    except Exception:
        logger.exception("Failed to enqueue initial_linkedin_scrape")

@app.get("/docs", tags=["Docs"], response_class=HTMLResponse)
def custom_docs():
    """Serve the bundled HTML docs file at /docs."""
    docs_path = Path(__file__).resolve().parent.parent / "api-docs.html"
    if not docs_path.exists():
        return HTMLResponse("<h1>Docs not found</h1>", status_code=404)
    return HTMLResponse(docs_path.read_text(encoding="utf-8"))

@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "ping": "/ping",
            "upload_resume": "/upload-resume",
            "analyze_resume": "/analyze-resume",
            "get_recommendations": "/get-recommendations",
            "recommend_by_skills": "/recommend-by-skills",
            "list_jobs": "/jobs"
        }
    }
