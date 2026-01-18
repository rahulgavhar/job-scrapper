from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
import logging
from app.services.file_service import save_pdf
from app.services.recommender import recommend_jobs_from_pdf, get_job_recommendations
from app.db.supabase_db import get_cached_jobs

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class SkillsRequest(BaseModel):
    skills: list[str]
    top_n: int = 5


class RecommendationResponse(BaseModel):
    success: bool
    extracted_skills: list[str] = []
    skills_count: int = 0
    recommendations: list[dict] = []
    recommendations_count: int = 0
    error: str = None


@router.get("/ping", tags=["Health"])
def ping():
    """Health check endpoint."""
    return {"message": "API is running"}


@router.get("/health", tags=["Health"])
def health_check():
    """API health check endpoint."""
    return {
        "status": "ok",
        "service": "Job Recommendation API",
        "version": "1.0.0"
    }


@router.post("/upload-resume", tags=["Resume"])
async def upload_resume(file: UploadFile = File(..., description="PDF resume file")):
    """
    Upload a resume PDF file and get job recommendations.

    - **file**: PDF file of the resume (required)

    Returns extracted skills and top matching jobs with scores.
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        file_path, storage_url = await save_pdf(file)

        print(f"\n{'='*60}")
        print(f"🔄 Processing resume: {file.filename}")
        print(f"📂 File path: {file_path}")
        print(f"{'='*60}\n")

        result = await recommend_jobs_from_pdf(file_path, top_n=5)

        if not result.get("success"):
            print(f"❌ Processing failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))

        recommendations = result.get("recommendations", [])
        extracted_skills = result.get("extracted_skills", result.get("skills", []))

        response = {
            "success": True,
            "message": "Resume processed successfully",
            "file_name": file.filename,
            "file_path": file_path,
            "storage_url": storage_url,
            "skills": extracted_skills,
            "recommendations": recommendations,
            "recommendations_count": len(recommendations)
        }

        if not recommendations:
            response["info"] = "No job recommendations found. Jobs are scraped automatically every 24 hours."

        return response
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/analyze-resume", tags=["Resume"], response_model=RecommendationResponse)
async def analyze_resume(file: UploadFile = File(..., description="PDF resume file")):
    """
    Upload a resume PDF and extract skills from it.
    Returns extracted skills list.
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        file_path, storage_url = await save_pdf(file)

        from app.services.pdf_parser import extract_text_from_pdf
        from app.services.skill_extractor import extract_skills

        text = await extract_text_from_pdf(file_path)
        skills = extract_skills(text, top_n=15)

        return {
            "success": True,
            "extracted_skills": skills,
            "skills_count": len(skills),
            "recommendations": [],
            "recommendations_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/get-recommendations", tags=["Recommendations"], response_model=RecommendationResponse)
async def get_recommendations(file: UploadFile = File(..., description="PDF resume file"), top_n: int = 5):
    """
    Upload resume, extract skills, and get job recommendations.
    Returns top matching jobs with match scores.
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        file_path, storage_url = await save_pdf(file)
        result = await recommend_jobs_from_pdf(file_path, top_n=top_n)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@router.post("/recommend-by-skills", tags=["Recommendations"])
def recommend_by_skills(request: SkillsRequest):
    """
    Get job recommendations based on provided skills.
    Useful for testing without uploading a resume.
    """
    try:
        result = get_job_recommendations(request.skills, top_n=request.top_n)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/jobs", tags=["Jobs"])
def list_all_jobs(skip: int = 0, limit: int = 10):
    """
    Get all available jobs from Supabase cache. Supports pagination.
    """
    try:
        all_jobs = get_cached_jobs() or []
        total_count = len(all_jobs)
        paginated_jobs = all_jobs[skip: skip + limit]
        return {
            "success": True,
            "total_jobs": total_count,
            "returned_jobs": len(paginated_jobs),
            "skip": skip,
            "limit": limit,
            "jobs": paginated_jobs,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")

# Removed public scraping endpoint; scraping now runs via cron/scheduler every 24 hours.
