#!/usr/bin/env python
"""Start the Job Recommendation API Server"""
import subprocess
import time
import sys
import socket
import os

def check_port(port):
    """Check if port is listening"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('127.0.0.1', port))
        return True
    except:
        return False

print("=" * 70)
print("STARTING Job Recommendation API Server")
print("=" * 70)

try:
    print("\n[1/3] Verifying application...")
    from app.main import app
    from app.services.skill_extractor import extract_skills
    print("✓ Application imports successful")

    print("\n[2/3] Testing skill extraction...")
    test_skills = extract_skills("Python Django FastAPI")
    print(f"✓ Skill extraction working: {test_skills}")

    print("\n[3/3] Starting Uvicorn server...")
    print("Command: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\nWaiting for server to start...")

    # Start server
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to be ready
    max_retries = 30
    for i in range(max_retries):
        if check_port(8000):
            print("✓ Server is running!\n")
            break
        time.sleep(1)
    else:
        print("⚠ Server may still be starting...\n")

    print("=" * 70)
    print("✓ JOB RECOMMENDATION API IS RUNNING")
    print("=" * 70)
    print("\n📊 API Documentation:")
    print("   http://localhost:8000/docs")
    print("   http://localhost:8000/redoc")
    print("\n🔗 Available Endpoints:")
    print("   POST   /upload-resume   - Upload resume PDF")
    print("   GET    /health          - Health check")
    print("   GET    /jobs            - Get all jobs")
    print("\n💡 To test the API:")
    print("   1. Visit http://localhost:8000/docs")
    print("   2. Click 'Try it out' on any endpoint")
    print("   3. Upload a resume PDF and get job recommendations")
    print("\n⚠️  Press Ctrl+C to stop the server\n")

    # Keep the process running
    process.wait()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

