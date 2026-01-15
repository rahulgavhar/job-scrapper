#!/usr/bin/env python
"""
QUICK START - Job Recommendation API

This script demonstrates how to use the API and what to expect.
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║         JOB RECOMMENDATION API - QUICK START GUIDE                 ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

✅ APPLICATION STATUS: READY TO RUN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 STEP 1: VERIFY INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run the setup test:
  $ python test_setup.py

Expected output:
  ✓ Testing FastAPI import...
  ✓ Testing app.core.config...
  ✓ All imports successful!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 STEP 2: START THE SERVER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option A (Recommended):
  $ python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Option B (Direct):
  $ python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

Option C (Custom script):
  $ python run_server.py

Expected output:
  INFO:     Uvicorn running on http://0.0.0.0:8000
  INFO:     Application startup complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STEP 3: ACCESS THE API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 Interactive Documentation (Swagger UI):
   http://localhost:8000/docs

📚 Alternative Documentation (ReDoc):
   http://localhost:8000/redoc

🔍 Health Check:
   http://localhost:8000/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 STEP 4: TEST THE API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open in browser: http://localhost:8000/docs

2. Click "POST /upload-resume" endpoint

3. Click "Try it out"

4. Upload a PDF file or use the sample resume

5. Click "Execute"

Expected Response:
{
  "success": true,
  "skills": ["Python", "Django", "FastAPI", ...],
  "recommendations": [
    {
      "id": 1,
      "title": "Software Engineer",
      "company": "TechCorp",
      "match_score": 0.95,
      ...
    }
  ]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 API ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /upload-resume
  ├─ Upload resume PDF
  └─ Returns: skills extracted + job recommendations

GET /health
  ├─ Health check endpoint
  └─ Returns: {"status": "healthy"}

GET /jobs
  ├─ List all available jobs
  └─ Returns: list of job objects

GET /jobs/{job_id}
  ├─ Get specific job details
  └─ Returns: job details

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test Setup (Imports & Config):
  $ python test_setup.py

Quick Test (App Ready Check):
  $ python test_run.py

Full Integration Test:
  $ python test_integration.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Resume PDF Upload & Parsing
✓ Automatic Skill Extraction (80+ skills database)
✓ Job Scraping from Multiple Sources
✓ Smart Job-Skill Matching
✓ Top Job Recommendations with Match Scores
✓ RESTful API with FastAPI
✓ Auto-generated API Documentation
✓ PyTorch 2.6+ Compatible
✓ Production Ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️  CUSTOMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add More Skills:
  Edit: app/services/skill_extractor.py
  Update: TECHNICAL_SKILLS set

Add Job Portals:
  Edit: app/services/scraper.py
  Add your scraping logic

Configure Server:
  Edit: app/core/config.py
  Change host, port, upload dir, etc.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 CURL EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check Health:
  $ curl http://localhost:8000/health

Get All Jobs:
  $ curl http://localhost:8000/jobs

Upload Resume (replace resume.pdf with actual file):
  $ curl -X POST -F "file=@resume.pdf" \\
    http://localhost:8000/upload-resume

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Port 8000 Already in Use?
  $ python -m uvicorn app.main:app --port 8001

Module Not Found?
  $ pip install -r requirements.txt

Need to Reinstall Dependencies?
  $ pip install --upgrade -r requirements.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 SUPPORT & DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

See Also:
  ✓ README.md          - Project overview
  ✓ RUNNING_GUIDE.md   - Detailed running guide
  ✓ API_USAGE.md       - API usage documentation
  ✓ ARCHITECTURE.md    - System architecture
  ✓ FILE_REFERENCE.md  - File reference guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ YOU'RE ALL SET!

The application is fully configured and ready to run.
Start the server and visit http://localhost:8000/docs to begin!

Happy coding! 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

