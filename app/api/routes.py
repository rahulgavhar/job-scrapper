from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
import json
from app.services.file_service import save_pdf
from app.services.recommender import recommend_jobs_from_pdf, get_job_recommendations
from app.db.fake_db import get_all_jobs

router = APIRouter()


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


@router.post("/upload-resume", tags=["Resume"])
async def upload_resume(file: UploadFile = File(..., description="PDF resume file")):
    """
    Upload a resume PDF file and get job recommendations.

    - **file**: PDF file of the resume (required)

    Returns extracted skills and top matching jobs with scores.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        # Save the file
        file_path = await save_pdf(file)

        # Get recommendations
        result = recommend_jobs_from_pdf(file_path, top_n=5, use_scraped=False)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))

        return {
            "success": True,
            "message": "Resume processed successfully",
            "file_name": file.filename,
            "skills": result.get("skills", []),
            "recommendations": result.get("recommendations", [])
        }
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

        file_path = await save_pdf(file)

        # Extract text and skills
        from app.services.pdf_parser import extract_text_from_pdf
        from app.services.skill_extractor import extract_skills

        text = extract_text_from_pdf(file_path)
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

        file_path = await save_pdf(file)
        result = recommend_jobs_from_pdf(file_path, top_n=top_n, use_scraped=False)

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
    Get all available jobs from the database.
    Supports pagination with skip and limit parameters.
    """
    try:
        all_jobs = get_all_jobs()
        total_count = len(all_jobs)

        # Apply pagination
        paginated_jobs = all_jobs[skip:skip + limit]

        return {
            "success": True,
            "total_jobs": total_count,
            "returned_jobs": len(paginated_jobs),
            "skip": skip,
            "limit": limit,
            "jobs": paginated_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")


@router.post("/scrape-jobs", tags=["Jobs"])
async def trigger_job_scraping(
    keyword: str = Query("python", description="Job search keyword"),
    location: str = Query("USA", description="Job location"),
    force_refresh: bool = Query(False, description="Bypass cache and force fresh scraping")
):
    """
    Scrape jobs from multiple online sources (GitHub, Jooble, Adzuna, RemoteOK, etc).
    Results are cached for 24 hours unless force_refresh=True, which bypasses cache.

    Parameters:
    - keyword: Job search keyword (default: "python")
    - location: Job location (default: "USA")
    - force_refresh: Bypass cache and force fresh scraping (default: False)
    """
    try:
        from app.services.scraper import scrape_all_jobs

        print(f"\n📮 API Request: /scrape-jobs?keyword={keyword}&location={location}&force_refresh={force_refresh}")
        scraped_jobs = scrape_all_jobs(keyword=keyword, location=location, force_refresh=force_refresh)

        if not scraped_jobs:
            print("⚠️  No jobs found, returning empty response")
            return {
                "success": False,
                "message": "No jobs found for the given criteria",
                "keyword": keyword,
                "location": location,
                "force_refresh": force_refresh,
                "jobs_count": 0,
                "jobs": []
            }

        return {
            "success": True,
            "message": f"Fetched {len(scraped_jobs)} jobs from multiple sources" + (" (fresh)" if force_refresh else ""),
            "keyword": keyword,
            "location": location,
            "force_refresh": force_refresh,
            "jobs_count": len(scraped_jobs),
            "jobs": scraped_jobs
        }
    except Exception as e:
        print(f"❌ Error in scrape-jobs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Job scraping failed: {str(e)}")


@router.post("/scrape-realtime", tags=["Jobs"])
async def scrape_realtime_jobs(
    keyword: str = Query("python", description="Job search keyword"),
    limit: int = Query(30, description="Max jobs per source")
):
    """
    Scrape REAL-TIME jobs from multiple sources and save to files.
    - Fetches from RemoteOK, GitHub Jobs, Adzuna
    - Saves to JSON and CSV
    - Returns file paths and job data

    Parameters:
    - keyword: Job search keyword (default: "python")
    - limit: Max jobs per source (default: 30)
    """
    try:
        from app.services.realtime_scraper import scrape_and_save

        print(f"\n📮 Real-time scrape request: keyword={keyword}, limit={limit}")

        # Scrape and save
        files = scrape_and_save(keyword=keyword, limit_per_source=limit)

        # Also read the JSON to return data
        json_path = Path(files.get("json", ""))
        jobs = []
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
                jobs = data.get("jobs", [])

        return {
            "success": True,
            "message": f"Scraped {len(jobs)} real-time jobs from multiple sources",
            "keyword": keyword,
            "jobs_count": len(jobs),
            "files": {
                "json": files.get("json"),
                "csv": files.get("csv")
            },
            "jobs": jobs
        }
    except Exception as e:
        print(f"❌ Real-time scrape error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Real-time scraping failed: {str(e)}")


@router.post("/scrape-linkedin", tags=["Jobs"])
async def scrape_linkedin_endpoint(
    position: str = Query("Python Developer", description="Job position to search"),
    location: str = Query("United States", description="Job location"),
    work_types: str = Query("Remote,Hybrid", description="Work types (comma-separated): On-site,Hybrid,Remote"),
    exp_levels: str = Query("Entry level,Associate", description="Experience levels (comma-separated): Internship,Entry level,Associate,Mid-Senior level"),
    time_filter: str = Query("Past month", description="Time filter: Past 24 hours, Past week, Past month"),
    max_pages: int = Query(2, description="Maximum pages to scrape (each page = 25 jobs)")
):
    """
    Scrape REAL LinkedIn jobs with Flair skill extraction.

    Parameters:
    - position: Job position (e.g., "Python Developer")
    - location: Job location (e.g., "United States")
    - work_types: Comma-separated work types (On-site, Hybrid, Remote)
    - exp_levels: Comma-separated experience levels
    - time_filter: Time filter for job posting
    - max_pages: Maximum pages to scrape (0-4 pages recommended)

    Returns:
    - CSV and JSON files with scraped jobs
    - Each job includes: title, company, location, description, extracted skills
    """
    try:
        from app.services.linkedin_scraper import scrape_linkedin_and_save
        import pandas as pd

        # Parse comma-separated values
        work_types_list = [w.strip() for w in work_types.split(",") if w.strip()]
        exp_levels_list = [e.strip() for e in exp_levels.split(",") if e.strip()]

        print(f"\n📮 LinkedIn scrape request: position={position}, location={location}")

        # Scrape and save
        files = scrape_linkedin_and_save(
            position=position,
            location=location,
            work_types=work_types_list,
            exp_levels=exp_levels_list,
            time_filter=time_filter,
            max_pages=max_pages
        )

        # Read saved data
        from pathlib import Path
        csv_path = Path(files.get("csv", ""))
        jobs = []

        if csv_path.exists():
            df = pd.read_csv(csv_path)
            jobs = df.to_dict('records')

        return {
            "success": True,
            "message": f"Scraped {len(jobs)} real LinkedIn jobs with skill extraction",
            "position": position,
            "location": location,
            "jobs_count": len(jobs),
            "files": {
                "csv": files.get("csv"),
                "json": files.get("json")
            },
            "jobs": jobs
        }
    except Exception as e:
        print(f"❌ LinkedIn scrape error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LinkedIn scraping failed: {str(e)}")


@router.get("/health", tags=["Health"])
def health_check():
    """API health check endpoint."""
    return {
        "status": "ok",
        "service": "Job Recommendation API",
        "version": "1.0.0"
    }
