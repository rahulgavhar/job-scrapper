# Job Recommendation API

A comprehensive backend API that analyzes resume PDFs, extracts skills using NLP, scrapes job listings, matches skills with jobs, and provides ranked job recommendations with match scores.

## Features

- **Resume Upload & Analysis**: Upload PDF resumes and extract skills using state-of-the-art NLP models
- **Skill Extraction**: Uses Flair Named Entity Recognition (NER) to identify technical and professional skills
- **Job Matching**: Advanced matching algorithm with similarity scoring (exact and fuzzy matching)
- **Job Scraping**: Integration-ready placeholders for scraping jobs from Indeed, LinkedIn, and other portals
- **Smart Recommendations**: Returns top job recommendations with match scores and matched skill counts
- **REST API**: Full-featured FastAPI with interactive Swagger documentation
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Docker Ready**: Multi-stage Dockerfile and docker-compose configuration included

## API Endpoints

### Health & Status
- **GET** `/` - Root endpoint with API information
- **GET** `/health` - Health check endpoint
- **GET** `/api/ping` - API ping endpoint

### Resume Management
- **POST** `/api/upload-resume` - Upload a resume PDF file
- **POST** `/api/analyze-resume` - Upload resume and extract skills

### Job Recommendations
- **POST** `/api/get-recommendations` - Upload resume and get job recommendations
- **POST** `/api/recommend-by-skills` - Get recommendations based on provided skills
- **POST** `/api/scrape-jobs` - Scrape jobs from online sources
- **GET** `/api/jobs` - List all available jobs with pagination

### Documentation
- **GET** `/api/docs` - Interactive Swagger UI documentation
- **GET** `/api/openapi.json` - OpenAPI schema

## Architecture

```
app/
├── main.py                 # FastAPI application setup
├── api/
│   └── routes.py          # API endpoint definitions
├── core/
│   └── config.py          # Application configuration
├── services/
│   ├── pdf_parser.py      # PDF text extraction
│   ├── skill_extractor.py # NLP skill extraction
│   ├── matcher.py         # Job-skill matching algorithm
│   ├── scraper.py         # Job scraping service
│   ├── recommender.py     # Recommendation orchestration
│   └── file_service.py    # File upload handling
└── db/
    └── fake_db.py         # Sample job database
```

## Technology Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **NLP**: Flair (Named Entity Recognition)
- **PDF Processing**: PyPDF2
- **Web Scraping**: BeautifulSoup4, Requests
- **Data Validation**: Pydantic
- **Containerization**: Docker, Docker Compose

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
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

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
curl -X POST "http://localhost:8000/api/get-recommendations" \
  -F "file=@resume.pdf" \
  -F "top_n=5"
```

**Response**:
```json
{
  "success": true,
  "extracted_skills": ["Python", "Django", "REST APIs", "SQL", "Git"],
  "skills_count": 5,
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

### 5. Scrape Jobs

```bash
curl -X POST "http://localhost:8000/api/scrape-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Python Developer",
    "location": "USA"
  }'
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

# Scraping
ENABLE_JOB_SCRAPING=True
SCRAPER_TIMEOUT=30
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
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── fake_db.py
│   └── services/
│       ├── __init__.py
│       ├── file_service.py
│       ├── pdf_parser.py
│       ├── skill_extractor.py
│       ├── matcher.py
│       ├── scraper.py
│       └── recommender.py
├── .env             # Environment configuration
├── .gitignore       # Git ignore file
├── Dockerfile       # Docker image configuration
├── requirements.txt # Python dependencies
└── README.md       # This file
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
- **PDF Processing**: Supports files up to 10MB by default
- **Caching**: Job scraping results are cached to avoid rate limiting

## Future Enhancements

- [ ] Real job portal integration (Indeed API, LinkedIn Scraper)
- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] Authentication and user profiles
- [ ] Resume storage and history
- [ ] Advanced filtering and sorting
- [ ] Job alerts and notifications
- [ ] Integration with job board APIs
- [ ] Semantic similarity using embeddings
- [ ] Machine learning model for better matching

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

### PDF Extraction Issues
- Ensure PDF is text-based (not scanned images)
- Check file size is under 10MB

### Skill Extraction Not Working
- Verify Flair model is downloaded: `kaliani/flair-ner-skill`
- Check internet connection for first-time model download

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

