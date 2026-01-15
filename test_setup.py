#!/usr/bin/env python
"""
Test script to validate API setup and dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all critical imports."""
    print("Testing imports...")

    try:
        print("✓ Testing FastAPI import...")
        from fastapi import FastAPI

        print("✓ Testing Pydantic import...")
        from pydantic import BaseModel

        print("✓ Testing app.core.config...")
        from app.core.config import settings

        print("✓ Testing app.db.fake_db...")
        from app.db.fake_db import JOBS_DB, get_all_jobs

        print("✓ Testing app.services.pdf_parser...")
        from app.services.pdf_parser import extract_text_from_pdf, save_resume

        print("✓ Testing app.services.matcher...")
        from app.services.matcher import match_jobs

        print("✓ Testing app.services.scraper...")
        from app.services.scraper import scrape_all_jobs

        print("✓ Testing app.services.recommender...")
        from app.services.recommender import recommend_jobs_from_pdf, get_job_recommendations

        print("✓ Testing app.api.routes...")
        from app.api.routes import router

        print("✓ Testing app.main...")
        from app.main import app

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from app.core.config import settings

        print(f"  App Name: {settings.APP_NAME}")
        print(f"  App Version: {settings.APP_VERSION}")
        print(f"  API Host: {settings.API_HOST}")
        print(f"  API Port: {settings.API_PORT}")
        print(f"  Upload Dir: {settings.UPLOAD_DIR}")
        print(f"  Max Skills Extracted: {settings.MAX_SKILLS_EXTRACTED}")

        print("\n✅ Configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False


def test_db():
    """Test database loading."""
    print("\nTesting database...")

    try:
        from app.db.fake_db import JOBS_DB, get_all_jobs

        jobs = get_all_jobs()
        print(f"  Total jobs in database: {len(jobs)}")
        if jobs:
            print(f"  Sample job: {jobs[0]['title']} at {jobs[0]['company']}")

        print("\n✅ Database loaded successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Database error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Job Recommendation API - Setup Validation")
    print("=" * 60)

    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "Database": test_db(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All validations passed! API is ready to run.")
        print("\nTo start the API, run:")
        print("  uvicorn app.main:app --reload")
        return 0
    else:
        print("\n❌ Some validations failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

