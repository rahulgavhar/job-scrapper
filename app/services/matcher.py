from difflib import SequenceMatcher
from app.db.supabase_db import get_cached_jobs


def normalize_skill(skill: str) -> str:
    """Normalize skill string for comparison."""
    return skill.lower().strip()


def calculate_skill_similarity(user_skill: str, job_skill: str) -> float:
    """
    Calculate similarity between two skills using SequenceMatcher.
    Returns a score between 0 and 1.
    """
    user_norm = normalize_skill(user_skill)
    job_norm = normalize_skill(job_skill)

    # Exact match
    if user_norm == job_norm:
        return 1.0

    # Partial match using SequenceMatcher
    similarity = SequenceMatcher(None, user_norm, job_norm).ratio()

    # Return similarity if above threshold (60%)
    return similarity if similarity > 0.6 else 0.0


def match_jobs(skills: list[str], top_n: int = 5) -> list[dict]:
    """
    Match extracted skills with jobs from Supabase using enhanced scoring.

    Args:
        skills (list[str]): List of skills extracted from resume
        top_n (int): Maximum number of job recommendations

    Returns:
        List of matching job dictionaries with match_score (0-100)
    """
    if not skills:
        return []

    # Get jobs from Supabase cache (all)
    jobs_db = get_cached_jobs() or []
    if not jobs_db:
        print("Warning: No jobs available in Supabase. Please scrape jobs first using /api/scrape-jobs-v2")
        return []

    matched_jobs = []

    # Score each job based on skill matches
    for job in jobs_db:
        # Skip if job is not a dict
        if not isinstance(job, dict):
            continue

        job_skills = job.get("skills", [])

        # Handle skills as string or list
        if isinstance(job_skills, str):
            job_skills = [s.strip() for s in job_skills.split(",")]

        if not job_skills:
            continue

        # Calculate match score
        total_similarity = 0.0
        matched_skills_count = 0

        for user_skill in skills:
            best_similarity = 0.0
            for job_skill in job_skills:
                similarity = calculate_skill_similarity(user_skill, job_skill)
                best_similarity = max(best_similarity, similarity)

            if best_similarity > 0:
                total_similarity += best_similarity
                matched_skills_count += 1

        # Calculate percentage match
        if matched_skills_count > 0:
            match_percentage = (total_similarity / len(skills)) * 100

            job_copy = job.copy()
            job_copy["match_score"] = round(match_percentage, 2)
            job_copy["matched_skills_count"] = matched_skills_count
            matched_jobs.append(job_copy)

    # Sort by score descending
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    return matched_jobs[:top_n]
