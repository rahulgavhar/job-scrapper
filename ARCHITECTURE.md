# Architecture & Design Documentation

## System Overview

The Job Recommendation API is a FastAPI-based backend system that processes resume PDFs, extracts skills using NLP, and matches them against available jobs to provide intelligent recommendations.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Application                         │
│              (Web, Mobile, or Desktop)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Server (Port 8000)                    │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                     API Routes                             │  │
│  │  • POST /api/upload-resume                                 │  │
│  │  • POST /api/analyze-resume                                │  │
│  │  • POST /api/get-recommendations                           │  │
│  │  • POST /api/recommend-by-skills                           │  │
│  │  • GET /api/jobs                                           │  │
│  │  • POST /api/scrape-jobs                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               Service Layer                                │  │
│  ├──────────────────┬───────────────────┬─────────────────────┤  │
│  │ File Service     │ PDF Parser        │ Skill Extractor     │  │
│  ├──────────────────┼───────────────────┼─────────────────────┤  │
│  │ • Save uploads   │ • Extract text    │ • Flair NER         │  │
│  │ • Validate files │ • PageHandling    │ • SkillIdentify     │  │
│  └──────────────────┴───────────────────┴─────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │          Matching & Recommendation Engine                  │  │
│  ├──────────────────┬───────────────────┬─────────────────────┤  │
│  │ Matcher          │ Recommender       │ Scraper             │  │
│  ├──────────────────┼───────────────────┼─────────────────────┤  │
│  │ • Scoring        │ • Orchestration   │ • Job portals       │  │
│  │ • Ranking        │ • Result ranking  │ • Caching           │  │
│  │ • Similarity     │ • Aggregation     │ • Filtering         │  │
│  └──────────────────┴───────────────────┴─────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  Data Layer                                │  │
│  │  • Fake Database (JOBS_DB)                                 │  │
│  │  • File Storage (uploads/)                                 │  │
│  │  • Cache (jobs_cache.json)                                 │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
    PyPDF2            Flair NER        BeautifulSoup
   (PDF Extract)   (Skill Extract)    (Job Scraping)
```

## Component Details

### 1. API Layer (routes.py)

**Responsibility**: Handle HTTP requests and responses

**Key Endpoints**:
- Upload & process resumes
- Extract skills from text
- Generate recommendations
- Manage jobs database

**Technologies**: FastAPI, Pydantic

**Error Handling**:
- 400: Bad Request (invalid file, missing parameters)
- 500: Internal Server Error (processing failures)

---

### 2. Service Layer

#### File Service (file_service.py)
```
Input: UploadFile (PDF)
    ↓
Validation (is PDF?)
    ↓
UUID Generation (unique filename)
    ↓
Save to Disk (uploads/)
    ↓
Output: file_path (string)
```

#### PDF Parser (pdf_parser.py)
```
Input: file_path (string)
    ↓
Open PDF (PyPDF2)
    ↓
Extract Text (all pages)
    ↓
Clean Text (strip whitespace)
    ↓
Output: text (string)
```

#### Skill Extractor (skill_extractor.py)
```
Input: text (string)
    ↓
Load Flair Model (kaliani/flair-ner-skill)
    ↓
Create Sentence Object
    ↓
Run NER Prediction
    ↓
Extract Named Entities (NER tags)
    ↓
Deduplicate & Limit (top_n)
    ↓
Output: skills (list[str])
```

**NER Model Details**:
- Model: `kaliani/flair-ner-ner-skill`
- Framework: Flair
- Task: Named Entity Recognition
- Extracts: Technical skills, tools, frameworks

**Limitations**:
- May miss domain-specific skills
- Requires training on custom skills for better accuracy

---

### 3. Matching Engine

#### Matcher (matcher.py)

**Algorithm**:
```
For each job in JOBS_DB:
  For each user_skill in extracted_skills:
    For each job_skill in job.skills:
      Calculate Similarity Score (0-1)
      Keep highest similarity
    
    If similarity > 0.6:
      Add to total_similarity
      Increment matched_count
  
  Calculate final_score = (total_similarity / skills_count) * 100
  
  If final_score > 0:
    Add to matched_jobs
    Store match_score and matched_count

Sort matched_jobs by match_score (descending)
Return top_n jobs
```

**Similarity Calculation**:
```python
def calculate_skill_similarity(user_skill, job_skill):
    if normalize(user_skill) == normalize(job_skill):
        return 1.0  # 100% match
    else:
        similarity = SequenceMatcher.ratio()
        return similarity if similarity > 0.6 else 0.0
```

**Example**:
```
User: ["Python", "Django", "SQL"]
Job: ["Python", "Django", "REST", "Git"]

Python vs Python: 1.0 ✓
Django vs Django: 1.0 ✓
SQL vs REST: 0.0 ✗
SQL vs Git: 0.0 ✗

Match Score = (2 matches / 3 skills) * 100 = 66.67%
```

---

### 4. Job Database

**Current Implementation**: In-memory fake database

```python
JOBS_DB = [
    {
        "id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "description": "...",
        "salary_range": "$120K - $150K",
        "skills": ["Python", "Django", "REST", "SQL", "Git"]
    },
    ...
]
```

**Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | int | Yes | Unique identifier |
| title | str | Yes | Job title |
| company | str | Yes | Company name |
| location | str | Yes | Work location |
| description | str | Yes | Job description |
| salary_range | str | No | Salary range |
| skills | list[str] | Yes | Required skills |

**Expansion to Database**:
For production, migrate to:
- PostgreSQL (relational)
- MongoDB (document-based)
- SQLite (lightweight)

---

### 5. Job Scraper

**Current Implementation**: Placeholder with caching

**Supported Sources**:
- Indeed (placeholder)
- LinkedIn (placeholder)
- Custom sources (extensible)

**Caching Strategy**:
```
Request to scrape jobs
    ↓
Check if cache exists?
    ├─ No → Scrape online
    │       Save to cache
    │       Return results
    └─ Yes → Use cached data
             Return results
```

**Future Enhancement**:
```python
# Real implementation example
def scrape_indeed(keyword, location):
    url = f"https://www.indeed.com/jobs?q={keyword}&l={location}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Parse job listings
    return jobs
```

---

### 6. Recommender Engine

**Flow**:
```
User Upload Resume (PDF)
    ↓
Save File
    ↓
Extract Text
    ↓
Extract Skills (NLP)
    ↓
Get Jobs (Database + Scraped)
    ↓
Match Skills with Jobs
    ↓
Rank by Match Score
    ↓
Return Top N Recommendations
    ↓
Send to Client
```

---

## Data Flow Diagrams

### Resume Analysis Flow
```
┌─────────────────────────────────────────────────────┐
│ User uploads resume.pdf                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
         ┌───────────────────┐
         │ File Validation   │
         │ • Check .pdf      │
         │ • Check size      │
         └───────┬───────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ↓                 ↓
    ✓ Valid         ✗ Invalid
        │                 │
        ↓                 ↓
    Save File      Return Error
        │                 │
        ↓                 └─── Return HTTP 400
  Extract Text
        │
        ↓
  Extract Skills (Flair NER)
        │
        ↓
  Match with Jobs
        │
        ↓
  Score & Rank
        │
        ↓
  Return Recommendations
```

### Skill Matching Flow
```
Input Skills: ["Python", "Django"]
Input Jobs: [Job1, Job2, Job3, ...]

For each Job:
  ┌─────────────────────────┐
  │ Job Skills: ["Python",  │
  │  "Django", "REST",      │
  │  "PostgreSQL"]          │
  └────────────┬────────────┘
               │
      ┌────────┴─────────┐
      │ Match Each Skill │
      │ Python: 100%     │
      │ Django: 100%     │
      │ Total: 200%      │
      └────────┬─────────┘
               │
      ┌────────┴──────────────────┐
      │ Calculate Score:          │
      │ 200% / 2 skills = 100%    │
      └────────┬──────────────────┘
               │
               ↓
        Store (Job, 100%)

Final: Sort by score, return top N
```

---

## Configuration Management

**app/core/config.py**:
```python
class Settings(BaseModel):
    # Application
    APP_NAME: str = "Job Recommendation API"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # NLP
    SKILLS_EXTRACTION_MODEL: str = "kaliani/flair-ner-skill"
    MAX_SKILLS_EXTRACTED: int = 15
    
    # Recommendations
    DEFAULT_TOP_N_RECOMMENDATIONS: int = 5
```

**Environment Variables (.env)**:
```env
DEBUG=False
API_PORT=8000
ENABLE_JOB_SCRAPING=True
```

---

## Error Handling Strategy

### Levels:

1. **Route Level** (routes.py)
   - HTTP exception handling
   - Status code mapping
   - Error serialization

2. **Service Level** (services/*.py)
   - Try-except blocks
   - Error logging
   - Exception propagation

3. **Validation Level** (Pydantic)
   - Input validation
   - Type checking
   - Schema validation

### Error Flow:
```
Exception Occurs
    ↓
Service catches & logs
    ↓
Returns error dict/raises HTTPException
    ↓
Route catches & formats
    ↓
Returns HTTP error response
    ↓
Client receives error
```

---

## Performance Considerations

### Bottlenecks & Solutions:

| Bottleneck | Impact | Solution |
|-----------|--------|----------|
| PDF text extraction | High for large PDFs | Parallel processing |
| Skill extraction (Flair) | Medium (model inference) | Model caching, quantization |
| Job matching (O(n*m)) | Medium (scales with jobs) | Indexing, caching |
| Scraping online | High (network I/O) | Async requests, caching |

### Optimization Strategies:
1. **Caching**: Cache job lists, skill extractions
2. **Indexing**: Use Elasticsearch for job search
3. **Async Processing**: Use async/await for I/O
4. **Batching**: Process multiple requests together
5. **Model Optimization**: Use lighter NLP models

---

## Security Considerations

1. **File Upload**
   - Validate file type
   - Limit file size
   - Virus scanning (ClamAV)
   - Quarantine folder

2. **Data Privacy**
   - Encrypt sensitive data
   - GDPR compliance
   - Data retention policies

3. **API Security**
   - Rate limiting
   - Authentication/Authorization
   - HTTPS/TLS
   - Input validation

4. **Infrastructure**
   - WAF (Web Application Firewall)
   - DDoS protection
   - Regular security audits

---

## Testing Strategy

### Test Types:

1. **Unit Tests**
   - Test individual functions
   - Mock external dependencies
   - File: `tests/test_services.py`

2. **Integration Tests**
   - Test service interactions
   - Use test database
   - File: `tests/test_integration.py`

3. **API Tests**
   - Test endpoints
   - Various input scenarios
   - File: `tests/test_api.py`

4. **Load Tests**
   - Test scalability
   - Tool: Locust, JMeter
   - File: `tests/test_load.py`

---

## Future Enhancements

### Phase 1: Core Improvements
- [ ] Real job portal integration
- [ ] PostgreSQL database
- [ ] User authentication
- [ ] Request caching

### Phase 2: Advanced Features
- [ ] Custom NLP model training
- [ ] Resume storage/history
- [ ] Job alerts
- [ ] User profiles

### Phase 3: ML Improvements
- [ ] Semantic similarity (embeddings)
- [ ] ML-based matching
- [ ] Skill clustering
- [ ] Trend analysis

### Phase 4: Scale & Reliability
- [ ] Kubernetes deployment
- [ ] Multi-region replication
- [ ] Advanced monitoring
- [ ] Auto-scaling

---

## References

- FastAPI Docs: https://fastapi.tiangolo.com/
- Flair NLP: https://github.com/flairNLP/flair
- PyPDF2: https://github.com/py-pdf/PyPDF2
- BeautifulSoup4: https://www.crummy.com/software/BeautifulSoup/

