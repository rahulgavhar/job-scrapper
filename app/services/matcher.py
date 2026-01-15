from difflib import SequenceMatcher
from app.db.fake_db import JOBS_DB


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
    Match extracted skills with jobs in the database using enhanced scoring.

    Args:
        skills (list[str]): List of skills extracted from resume
        top_n (int): Maximum number of job recommendations

    Returns:
        List of matching job dictionaries with match_score (0-100)
    """
    if not skills:
        return []

    matched_jobs = []

    # Score each job based on skill matches
    for job in JOBS_DB:
        job_skills = job.get("skills", [])

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

