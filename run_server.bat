@echo off
REM Quick start script for the Job Scraper API (Windows)

echo ==================================================
echo JOB RECOMMENDATION API - STARTUP
echo ==================================================
echo.

echo 📦 Installing dependencies...
pip install -r requirements.txt -q

echo ✓ Dependencies installed
echo.

echo 🚀 Starting server on http://127.0.0.1:8000
echo 📖 API docs: http://127.0.0.1:8000/docs
echo 📖 Redoc: http://127.0.0.1:8000/redoc
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

