from app.services.pdf_parser import extract_text_from_pdf
from app.services.skill_extractor import extract_skills
from app.services.matcher import match_jobs


async def recommend_jobs_from_pdf(file_path: str, top_n: int = 5) -> dict:
    """
    Main function to generate job recommendations from a resume PDF.

    Args:
        file_path (str): Path to the uploaded PDF resume
        top_n (int): Number of job recommendations to return

    Returns:
        Dictionary containing extracted skills and recommended jobs with match scores
    """
    try:
        # Step 1: Extract text from PDF
        print(f"📄 Extracting text from: {file_path}")
        resume_text = await extract_text_from_pdf(file_path)

        if not resume_text:
            print("❌ No text extracted from PDF")
            return {
                "success": False,
                "error": "Could not extract text from PDF",
                "skills": [],
                "recommendations": []
            }

        print(f"✓ Extracted {len(resume_text)} characters from PDF")
        print(f"📝 First 200 chars: {resume_text[:200]}")

        # Step 2: Extract skills from resume text
        skills = extract_skills(resume_text, top_n=15)
        print(f"🔍 Extracted {len(skills)} skills: {skills}")

        if not skills:
            print("❌ No skills extracted from resume text")
            return {
                "success": False,
                "error": "Could not extract skills from resume. Please ensure your resume contains technical skills like Python, Java, SQL, etc.",
                "skills": [],
                "recommendations": [],
                "debug_info": {
                    "text_length": len(resume_text),
                    "text_sample": resume_text[:500]
                }
            }

        # Step 3: Match skills with jobs from Supabase cache
        # Jobs are scraped automatically every 24h via Celery background task
        # match_jobs() internally gets jobs from Supabase via get_cached_jobs()
        print(f"🎯 Matching {len(skills)} skills with available jobs...")
        recommended_jobs = match_jobs(skills, top_n=top_n)
        print(f"✓ Found {len(recommended_jobs)} job recommendations")

        return {
            "success": True,
            "extracted_skills": skills,
            "skills_count": len(skills),
            "recommendations": recommended_jobs,
            "recommendations_count": len(recommended_jobs)
        }

    except Exception as e:
        print(f"❌ EXCEPTION in recommend_jobs_from_pdf: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Processing error: {str(e)}",
            "skills": [],
            "recommendations": [],
            "error_type": type(e).__name__
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

