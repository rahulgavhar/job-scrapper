from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
import random
import time
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
    """Start scheduler for periodic scraping and archiving."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        from app.services.linkedin_scraper_simple import scrape_linkedin_jobs
        from app.db.supabase_db import save_jobs, archive_old_caches

        scheduler = BackgroundScheduler()

        def scrape_task():
            positions = [
                "Software Engineer", "Backend Developer", "Frontend Developer", "Data Scientist",
                "Full Stack Developer", "DevOps Engineer", "Machine Learning Engineer", "Data Engineer",
            ]
            locations = [
                "United States", "India", "Canada", "United Kingdom", "Germany", "Australia",
                "San Francisco", "New York", "London", "Bangalore", "Berlin", "Sydney",
            ]

            combos = [(random.choice(positions), random.choice(locations)) for _ in range(6)]
            random.shuffle(combos)

            for pos, loc in combos:
                delay = random.uniform(60, 120)  # enforce >=1 minute gap between targets
                time.sleep(delay)
                jobs = scrape_linkedin_jobs(pos, loc, max_results=20)
                if jobs:
                    save_jobs(jobs, pos, loc)
            archive_old_caches()

        # Run once immediately on startup
        try:
            scrape_task()
            logger.info("Ran initial scrape_task on startup")
        except Exception:
            logger.exception("Initial scrape_task failed")

        scheduler.add_job(
            scrape_task,
            IntervalTrigger(hours=24, jitter=180),
            id="scrape_every_24h",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Scheduler started with job scrape_every_24h")
    except Exception:
        logger.exception("Scheduler failed to start")

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
