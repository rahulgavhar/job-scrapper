#!/usr/bin/env python
"""Simple test to check if the app can run"""
import sys
import os

print("=" * 60)
print("Testing Job Recommendation API")
print("=" * 60)

try:
    print("\n[1/5] Importing dependencies...")
    from app.main import app
    print("✓ Successfully imported app")

    print("\n[2/5] Testing FastAPI app object...")
    assert app is not None
    print(f"✓ App created: {app}")

    print("\n[3/5] Checking routes...")
    routes = [route.path for route in app.routes]
    print(f"✓ Available routes: {routes}")

    print("\n[4/5] Testing skill extraction...")
    from app.services.skill_extractor import extract_skills
    test_text = "Python Django FastAPI REST APIs Machine Learning"
    skills = extract_skills(test_text)
    print(f"✓ Extracted skills: {skills}")

    print("\n[5/5] All tests passed!")
    print("\n" + "=" * 60)
    print("✓ Application is ready to run")
    print("=" * 60)
    print("\nYou can now start the server with:")
    print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nThen visit: http://localhost:8000/docs")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

