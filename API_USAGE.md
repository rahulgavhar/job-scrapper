# API Usage Guide

## Quick Start

### 1. Installation & Setup

```bash
# Clone or navigate to project directory
cd job-scrapper

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/api/docs`

### 2. Test the Setup

```bash
# Run setup validation
python test_setup.py

# Run integration tests
python test_integration.py
```

## API Endpoints Reference

### Health & Information

#### Check API Status
```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "Job Recommendation API"
}
```

#### Get API Information
```bash
GET /
```

Response includes all available endpoints.

### Resume Processing

#### Upload Resume
```bash
POST /api/upload-resume
Content-Type: multipart/form-data

file: <PDF file>
```

Example using curl:
```bash
curl -X POST "http://localhost:8000/api/upload-resume" \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "success": true,
  "message": "Resume uploaded successfully",
  "file_path": "uploads/123e4567-e89b-12d3-a456-426614174000.pdf"
}
```

#### Extract Skills from Resume
```bash
POST /api/analyze-resume
Content-Type: multipart/form-data

file: <PDF file>
```

Example:
```bash
curl -X POST "http://localhost:8000/api/analyze-resume" \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "success": true,
  "extracted_skills": ["Python", "Django", "REST API", "SQL", "Git"],
  "skills_count": 5,
  "recommendations": [],
  "recommendations_count": 0
}
```

### Job Recommendations

#### Get Recommendations from Resume
```bash
POST /api/get-recommendations
Content-Type: multipart/form-data

file: <PDF file>
top_n: 5 (optional, default: 5)
```

Example:
```bash
curl -X POST "http://localhost:8000/api/get-recommendations?top_n=5" \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "success": true,
  "extracted_skills": ["Python", "Django", "REST API"],
  "skills_count": 3,
  "recommendations": [
    {
      "id": 1,
      "title": "Software Engineer",
      "company": "TechCorp",
      "location": "San Francisco, CA",
      "description": "Develop and maintain web applications...",
      "salary_range": "$120,000 - $150,000",
      "skills": ["Python", "Django", "REST", "SQL", "Git"],
      "match_score": 100.0,
      "matched_skills_count": 3
    }
  ],
  "recommendations_count": 1
}
```

#### Get Recommendations by Skills
```bash
POST /api/recommend-by-skills
Content-Type: application/json

{
  "skills": ["Python", "Machine Learning", "SQL"],
  "top_n": 3
}
```

Example:
```bash
curl -X POST "http://localhost:8000/api/recommend-by-skills" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "Django", "PostgreSQL"],
    "top_n": 5
  }'
```

Response:
```json
{
  "success": true,
  "input_skills": ["Python", "Django", "PostgreSQL"],
  "recommendations": [
    {
      "id": 6,
      "title": "Full Stack Developer",
      "company": "WebDynamics",
      "location": "Boston, MA",
      "description": "Build end-to-end web applications...",
      "salary_range": "$125,000 - $155,000",
      "skills": ["Python", "React", "PostgreSQL", "REST", "Git", "JavaScript"],
      "match_score": 66.67,
      "matched_skills_count": 2
    }
  ],
  "recommendations_count": 1
}
```

### Job Management

#### List All Jobs
```bash
GET /api/jobs?skip=0&limit=10
```

Example:
```bash
curl "http://localhost:8000/api/jobs?skip=0&limit=5"
```

Response:
```json
{
  "success": true,
  "total_jobs": 8,
  "returned_jobs": 5,
  "skip": 0,
  "limit": 5,
  "jobs": [...]
}
```

#### Scrape Jobs from Online Sources
```bash
POST /api/scrape-jobs
Content-Type: application/json

{
  "keyword": "Python Developer",
  "location": "USA"
}
```

Example:
```bash
curl -X POST "http://localhost:8000/api/scrape-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Python Developer",
    "location": "Remote"
  }'
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "recommendations": [...]
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 500 | Server Error |

## Error Messages

| Error | Solution |
|-------|----------|
| "Only PDF files are allowed" | Ensure you're uploading a .pdf file |
| "Could not extract text from PDF" | Ensure PDF is not corrupted and contains text (not image) |
| "Could not extract skills from resume" | Resume text doesn't contain recognizable skills |
| "File path is required" | Make sure file_path parameter is provided |

## Rate Limiting

Currently no rate limiting is implemented. For production use, add rate limiting middleware:

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

app.add_middleware(
    RateLimiter,
    key_func=get_remote_address,
    default_limits="100/minute"
)
```

## Authentication

No authentication is currently required. For production, add API key or OAuth2:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/get-recommendations")
async def get_recommendations(credentials: HTTPAuthCredentials = Depends(security)):
    # Validate credentials
    pass
```

## Performance Tips

1. **Cache Results**: Cache job recommendations for frequent skill sets
2. **Batch Processing**: Process multiple resumes in batches
3. **Async Uploads**: Use async processing for large files
4. **Database**: Migrate from fake_db to PostgreSQL for better performance

## Troubleshooting

### Port 8000 Already in Use
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

### PDF Extraction Issues
- Ensure PDF is text-based (not scanned images)
- Check file size (max 10MB)
- Try opening PDF in a text editor to verify it contains text

### Skill Extraction Not Working
- Check internet connection (Flair model downloads from HuggingFace)
- Verify Flair is installed: `pip install flair`
- Try restarting the API

### No Jobs Found
- Check database has jobs: `python test_integration.py`
- Verify skills match job requirements
- Increase `top_n` parameter to see more results

## Testing with Postman

1. Import the API into Postman
2. Use `{{base_url}}` = `http://localhost:8000`
3. Test endpoints with provided examples

## Docker Usage

```bash
# Build image
docker build -t job-recommendation-api .

# Run container
docker run -p 8000:8000 job-recommendation-api

# Or use docker-compose
docker-compose up
```

## Next Steps

1. Customize skill extraction by training your own Flair model
2. Integrate with real job portals (Indeed, LinkedIn APIs)
3. Add user authentication
4. Implement job alerts and notifications
5. Add resume storage and history
6. Deploy to cloud (AWS, GCP, Azure)

