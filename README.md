# Job Recommendation API

A comprehensive backend API that analyzes resume PDFs, extracts skills using NLP, scrapes job listings, matches skills with jobs, and provides ranked job recommendations with match scores.

## Features

- **Resume Upload & Analysis**: Upload PDF resumes and extract skills using state-of-the-art NLP models
- **Skill Extraction**: Uses Flair Named Entity Recognition (NER) to identify technical and professional skills
- **Job Matching**: Advanced matching algorithm with similarity scoring (exact and fuzzy matching)
- **LinkedIn Job Scraping**: Automated background scraping from LinkedIn every 24 hours using Celery
- **Smart Recommendations**: Returns top job recommendations with match scores and matched skill counts
- **Cloud Storage**: Supabase integration for resume storage and job caching
- **Background Tasks**: Celery-powered task queue for non-blocking job scraping
- **REST API**: Full-featured FastAPI with interactive Swagger documentation
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Docker Ready**: Multi-stage Dockerfile and docker-compose configuration included
- **Scalable Architecture**: Production-ready with Celery workers and Redis message broker

## API Endpoints

### Health & Status
- **GET** `/ping` - API ping endpoint
- **GET** `/health` - Health check endpoint

### Resume Management
- **POST** `/api/upload-resume` - Upload a resume PDF file and get recommendations
- **POST** `/api/analyze-resume` - Upload resume and extract skills only

### Job Recommendations
- **POST** `/api/get-recommendations` - Upload resume and get job recommendations
- **POST** `/api/recommend-by-skills` - Get recommendations based on provided skills
- **GET** `/api/jobs` - List all available jobs with pagination

### Documentation
- **GET** `/api/docs` - Interactive Swagger UI documentation

## Architecture

```
app/
├── main.py                      # FastAPI application setup
├── celery_app.py                # Celery configuration
├── api/
│   └── routes.py                # API endpoint definitions
├── core/
│   └── config.py                # Application configuration
├── services/
│   ├── pdf_parser.py            # PDF text extraction
│   ├── skill_extractor.py       # NLP skill extraction
│   ├── matcher.py               # Job-skill matching algorithm
│   ├── linkedin_scraper_simple.py # LinkedIn job scraping
│   ├── recommender.py           # Recommendation orchestration
│   ├── file_service.py          # File upload handling
│   ├── supabase_storage.py      # Cloud storage integration
│   └── tasks.py                 # Celery background tasks
└── db/
    └── supabase_db.py           # Supabase database integration
```

## Technology Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **NLP**: Flair (Named Entity Recognition)
- **PDF Processing**: PyPDF2
- **Web Scraping**: BeautifulSoup4, Requests, AioHTTP
- **Data Validation**: Pydantic
- **Cloud Storage**: Supabase
- **Task Queue**: Celery
- **Message Broker**: Redis
- **Scheduler**: APScheduler
- **Containerization**: Docker, Docker Compose
- **HTTP Client**: HTTPX

## Installation

### Prerequisites
- Python 3.11+
- pip or conda
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone the repository**
```bash
cd job-scrapper
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the API**

**Option A: Production Mode (Celery + FastAPI)**
```bash
# Requires Redis running
# Redis should be accessible at redis://localhost:6379/0 (default)
python start_api.py
```
This starts both Celery worker and FastAPI server with unified logging and background job scraping.

**Option B: Development Mode (FastAPI only)**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

> **Note**: For production deployment with background job scraping via Celery, use `python start_api.py`. Ensure Redis is running and accessible. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

### Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access the API**
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/api/docs`

## Usage Examples

### 1. Upload Resume and Get Recommendations

```bash
curl -X POST "http://localhost:8000/api/upload-resume" \
  -F "file=@resume.pdf"
```

**Response**:
```json
{
  "success": true,
  "file_name": "resume.pdf",
  "file_path": "/path/to/resume.pdf",
  "storage_url": "https://supabase.../resume.pdf",
  "skills": ["Python", "Django", "REST APIs", "SQL", "Git"],
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
      "matched_skills_count": 5
    }
  ],
  "recommendations_count": 1
}
```

### 2. Get Recommendations by Skills

```bash
curl -X POST "http://localhost:8000/api/recommend-by-skills" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "Machine Learning", "SQL"],
    "top_n": 3
  }'
```

### 3. Extract Skills from Resume

```bash
curl -X POST "http://localhost:8000/api/analyze-resume" \
  -F "file=@resume.pdf"
```

### 4. List All Jobs

```bash
curl "http://localhost:8000/api/jobs?skip=0&limit=10"
```

### 5. Health Check

```bash
curl "http://localhost:8000/health"
```

## Configuration

All settings can be configured via `.env` file:

```env
# Application
APP_NAME=Job Recommendation API
APP_VERSION=1.0.0
DEBUG=False

# Server
API_HOST=0.0.0.0
API_PORT=8000

# NLP Model
SKILLS_EXTRACTION_MODEL=kaliani/flair-ner-skill
MAX_SKILLS_EXTRACTED=15

# Recommendations
DEFAULT_TOP_N_RECOMMENDATIONS=5
MIN_MATCH_SCORE=0.0

# File Upload
MAX_UPLOAD_SIZE=52428800

# Supabase Configuration
SUPABASE_URL=https://your-supabase.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_STORAGE_BUCKET=resumes
USE_SUPABASE_STORAGE=True

# CORS Client URLs
CLIENT_URL1=https://your-client-1.com
CLIENT_URL2=https://your-client-2.com
CLIENT_URL3=https://your-client-3.com

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Scraper
SCRAPER_TIMEOUT=30
ENABLE_JOB_SCRAPING=True
```

## Matching Algorithm

The job matching algorithm uses an advanced scoring system:

1. **Skill Normalization**: Converts all skills to lowercase for comparison
2. **Similarity Calculation**: Uses sequence matching to find similar skills
3. **Weighted Scoring**: 
   - Exact matches: 100% score
   - Partial matches (>60% similarity): Proportional score
   - No matches: 0% score
4. **Final Score**: Average of all matched skills × 100

Example:
- User skills: ["Python", "Django"]
- Job skills: ["python", "django", "rest"]
- Match score: 100% (both skills matched exactly)

## Project Structure

```
job-scrapper/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── celery_app.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── supabase_db.py
│   └── services/
│       ├── __init__.py
│       ├── file_service.py
│       ├── pdf_parser.py
│       ├── skill_extractor.py
│       ├── matcher.py
│       ├── recommender.py
│       ├── supabase_storage.py
│       ├── linkedin_scraper_simple.py
│       └── tasks.py
├── start_api.py         # Entry point for production (with Celery)
├── .env                 # Environment configuration
├── .gitignore           # Git ignore file
├── Dockerfile           # Docker image configuration
├── requirements.txt     # Python dependencies
├── ARCHITECTURE.md      # Architecture documentation
└── README.md           # This file
```

## API Response Format

All responses follow a consistent JSON format:

```json
{
  "success": true/false,
  "data": {...},
  "error": null,
  "message": "Success message"
}
```

## Error Handling

The API provides detailed error messages:

```json
{
  "detail": "Only PDF files are allowed"
}
```

Common HTTP status codes:
- `200 OK` - Successful request
- `400 Bad Request` - Invalid input (e.g., non-PDF file)
- `500 Internal Server Error` - Server error

## Performance Considerations

- **Skill Extraction**: Uses cached Flair models for faster inference
- **Job Matching**: O(n*m) complexity where n = skills, m = jobs
- **PDF Processing**: Supports files up to 50MB
- **Background Processing**: Celery workers handle LinkedIn scraping without blocking API requests
- **Job Caching**: Supabase integration caches job listings to minimize scraping and API calls
- **Redis Optimization**: Redis message broker ensures fast task queuing and result retrieval
- **Async Operations**: Uses async/await for non-blocking file uploads and processing

## Future Enhancements

- [ ] Multiple job portal integration (Indeed API, Glassdoor, etc.)
- [ ] Advanced filtering and sorting options
- [ ] Job alerts and email notifications
- [ ] Semantic similarity using embeddings (BERT/GPT)
- [ ] Machine learning model for improved matching
- [ ] User authentication and profiles
- [ ] Resume versioning and history
- [ ] Skill validation and certifications
- [ ] Salary prediction based on skills

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001
```

### Redis Connection Error
```bash
# Ensure Redis is running
redis-cli ping  # Should return "PONG"

# If Redis is not installed, install via:
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Linux: apt-get install redis-server

# Update .env if Redis is on different host/port
CELERY_BROKER_URL=redis://your-redis-host:6379/0
```

### Celery Tasks Not Running
- Verify Redis is accessible
- Check Celery worker logs for errors
- Ensure `python start_api.py` is running (not just `uvicorn`)

### PDF Extraction Issues
- Ensure PDF is text-based (not scanned images)
- Check file size is under 50MB
- Verify file is a valid PDF

### Skill Extraction Not Working
- Verify Flair model is downloaded: `kaliani/flair-ner-skill`
- Check internet connection for first-time model download
- Ensure torch is properly installed

### Supabase Connection Error
- Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env
- Check Supabase project is active
- Ensure storage bucket exists and is accessible

### Docker Build Issues
- Clear Docker cache: `docker system prune`
- Rebuild: `docker-compose build --no-cache`

## License

MIT License - feel free to use this project for personal or commercial use.

## Support

For issues and questions:
1. Check the API documentation at `/api/docs`
2. Review error messages in console output
3. Check `.env` configuration

## Contributors

Built with ❤️ for job seekers everywhere.

