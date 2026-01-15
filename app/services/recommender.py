from app.services.pdf_parser import extract_text_from_pdf
from app.services.skill_extractor import extract_skills
from app.services.matcher import match_jobs
from app.services.scraper import scrape_all_jobs
from app.db.fake_db import JOBS_DB


def recommend_jobs_from_pdf(file_path: str, top_n: int = 5, use_scraped: bool = False) -> dict:
    """
    Main function to generate job recommendations from a resume PDF.

    Args:
        file_path (str): Path to the uploaded PDF resume
        top_n (int): Number of job recommendations to return
        use_scraped (bool): Whether to include scraped jobs

    Returns:
        Dictionary containing extracted skills and recommended jobs with match scores
    """
    try:
        # Step 1: Extract text from PDF
        resume_text = extract_text_from_pdf(file_path)

        if not resume_text:
            return {
                "success": False,
                "error": "Could not extract text from PDF",
                "skills": [],
                "recommendations": []
            }

        # Step 2: Extract skills from resume text
        skills = extract_skills(resume_text, top_n=15)

        if not skills:
            return {
                "success": False,
                "error": "Could not extract skills from resume",
                "skills": [],
                "recommendations": []
            }

        # Step 3: Get jobs to match against
        jobs_to_match = list(JOBS_DB)  # Always include database jobs

        if use_scraped:
            try:
                scraped_jobs = scrape_all_jobs()
                jobs_to_match.extend(scraped_jobs)
            except Exception as e:
                print(f"Warning: Failed to scrape jobs: {e}")

        # Step 4: Match skills with available jobs
        recommended_jobs = match_jobs(skills, top_n=top_n)

        return {
            "success": True,
            "extracted_skills": skills,
            "skills_count": len(skills),
            "recommendations": recommended_jobs,
            "recommendations_count": len(recommended_jobs)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "skills": [],
            "recommendations": []
        }


def get_job_recommendations(skills: list[str], top_n: int = 5) -> dict:
    """
    Get job recommendations based on provided skills.

    Args:
        skills (list[str]): List of skills to match
        top_n (int): Number of recommendations to return

    Returns:
        Dictionary with recommendations and metadata
    """
    try:
        if not skills:
            return {
                "success": False,
                "error": "No skills provided",
                "recommendations": []
            }

        recommended_jobs = match_jobs(skills, top_n=top_n)

        return {
            "success": True,
            "input_skills": skills,
            "recommendations": recommended_jobs,
            "recommendations_count": len(recommended_jobs)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "recommendations": []
        }

