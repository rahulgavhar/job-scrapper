"""
Sample API usage and integration tests.
Run this to test the API endpoints.
"""

import json
from app.services.matcher import match_jobs
from app.services.recommender import get_job_recommendations
from app.db.fake_db import JOBS_DB, get_all_jobs


def test_matcher():
    """Test the job matcher."""
    print("\n" + "="*60)
    print("Testing Job Matcher")
    print("="*60)

    # Test skills
    test_skills = ["Python", "Django", "REST API", "SQL"]

    print(f"\nSearching jobs for skills: {test_skills}")

    recommendations = match_jobs(test_skills, top_n=5)

    if recommendations:
        print(f"Found {len(recommendations)} matching jobs:\n")
        for i, job in enumerate(recommendations, 1):
            print(f"{i}. {job['title']} at {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Match Score: {job['match_score']}%")
            print(f"   Matched Skills: {job['matched_skills_count']}")
            print()
    else:
        print("No matching jobs found.")


def test_recommender():
    """Test the recommender."""
    print("\n" + "="*60)
    print("Testing Recommender")
    print("="*60)

    test_skills = ["JavaScript", "React", "CSS", "HTML"]

    print(f"\nGetting recommendations for skills: {test_skills}\n")

    result = get_job_recommendations(test_skills, top_n=3)

    print(json.dumps(result, indent=2))


def test_all_jobs():
    """Display all jobs in database."""
    print("\n" + "="*60)
    print("All Available Jobs in Database")
    print("="*60)

    jobs = get_all_jobs()

    print(f"\nTotal jobs: {len(jobs)}\n")

    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job.get('salary_range', 'N/A')}")
        print(f"   Skills: {', '.join(job['skills'])}")
        print()


def test_skill_matching_algorithm():
    """Test the skill matching algorithm details."""
    print("\n" + "="*60)
    print("Testing Skill Matching Algorithm")
    print("="*60)

    from app.services.matcher import calculate_skill_similarity, normalize_skill

    test_pairs = [
        ("Python", "python"),
        ("Python", "Python"),
        ("JavaScript", "Java"),
        ("React", "React.js"),
        ("Django", "django"),
        ("REST", "REST API"),
    ]

    print("\nSkill Similarity Scores:\n")
    print(f"{'User Skill':<20} {'Job Skill':<20} {'Similarity':<15}")
    print("-" * 55)

    for user_skill, job_skill in test_pairs:
        score = calculate_skill_similarity(user_skill, job_skill)
        print(f"{user_skill:<20} {job_skill:<20} {score:.2%}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Job Recommendation API - Integration Tests")
    print("="*60)

    try:
        test_all_jobs()
        test_skill_matching_algorithm()
        test_matcher()
        test_recommender()

        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

