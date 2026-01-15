from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for job recommendations based on resume analysis"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

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
            "list_jobs": "/jobs",
            "scrape_jobs": "/scrape-jobs"
        }
    }

