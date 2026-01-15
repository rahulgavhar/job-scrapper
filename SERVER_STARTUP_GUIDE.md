# ✅ SERVER STARTUP GUIDE

## 🚀 QUICK START (Windows)

### **Option 1: Run Batch File (Easiest)**
```bash
cd C:\Users\rahul\PycharmProjects\PythonProject\job-scrapper
run_server.bat
```

### **Option 2: Run Directly in PowerShell**
```powershell
cd C:\Users\rahul\PycharmProjects\PythonProject\job-scrapper
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### **Option 3: Run in CMD**
```cmd
cd C:\Users\rahul\PycharmProjects\PythonProject\job-scrapper
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📋 SETUP CHECKLIST

### **1. Install Dependencies (One-Time)**
```bash
pip install -r requirements.txt
```

### **2. Verify Installation**
```bash
python test_server_startup.py
```

Expected output:
```
✓ Test 1: Import FastAPI app
  ✅ App imported successfully

✓ Test 2: Check API routes
  ✅ Found 11 routes

✓ Test 3: Verify dependencies
  ✅ requests: installed
  ✅ pandas: installed
  ✅ beautifulsoup4: installed

✓ Test 4: Check Flair (optional)
  ✅ Flair installed

============================================================
✅ ALL TESTS PASSED - SERVER READY!
============================================================
```

### **3. Start Server**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## 🌐 ACCESS API

### **Swagger UI (Interactive)**
```
http://127.0.0.1:8000/docs
```

### **ReDoc (Alternative)**
```
http://127.0.0.1:8000/redoc
```

### **Health Check**
```bash
curl http://127.0.0.1:8000/health
```

---

## 📊 AVAILABLE ENDPOINTS

### **Health & Info**
- `GET /health` - Health check
- `GET /` - API info

### **Resume Processing**
- `POST /upload-resume` - Upload resume + get recommendations
- `POST /analyze-resume` - Extract skills from resume
- `POST /get-recommendations` - Get recommendations (custom params)

### **Job Scraping**
- `POST /scrape-jobs` - Scrape from cached/API sources
- `POST /scrape-realtime` - Scrape from multiple APIs (RemoteOK, GitHub, Adzuna)
- `POST /scrape-linkedin` - **Scrape LinkedIn jobs with Flair skill extraction**

### **Job Recommendations**
- `POST /recommend-by-skills` - Get recommendations by skills
- `GET /jobs` - List all jobs (paginated)

---

## 🧪 TEST ENDPOINTS

### **1. Health Check**
```bash
curl http://127.0.0.1:8000/health
```

### **2. Scrape Real-Time Jobs**
```bash
curl -X POST "http://127.0.0.1:8000/scrape-realtime?keyword=python&limit=30"
```

### **3. Scrape LinkedIn Jobs**
```bash
curl -X POST "http://localhost:8000/scrape-linkedin?position=Python%20Developer&max_pages=1"
```

### **4. Recommend by Skills**
```bash
curl -X POST "http://127.0.0.1:8000/recommend-by-skills" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "Django", "REST"], "top_n": 5}'
```

---

## ❌ TROUBLESHOOTING

### **Issue: Port 8000 Already in Use**
```bash
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### **Issue: Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Issue: Flair Model Download Slow**
- First API call may take 5-10 minutes (downloads 500MB model)
- Be patient, it only happens once
- Model is cached after first download

### **Issue: LinkedIn Scraper Returns No Jobs**
- LinkedIn structure changes frequently
- Try different search terms
- Check if LinkedIn website loads normally
- Wait 24-48 hours if you get 429 (too many requests)

---

## 📁 PROJECT STRUCTURE

```
job-scrapper/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── api/
│   │   └── routes.py           # All endpoints
│   ├── services/
│   │   ├── scraper.py          # General scraper
│   │   ├── realtime_scraper.py # Real-time scraper
│   │   ├── linkedin_scraper.py # LinkedIn scraper (NEW!)
│   │   ├── pdf_parser.py       # PDF parsing
│   │   ├── skill_extractor.py  # Skill extraction
│   │   ├── matcher.py          # Job matching
│   │   ├── recommender.py      # Recommendations
│   │   └── file_service.py     # File handling
│   ├── db/
│   │   └── fake_db.py          # Sample jobs
│   └── core/
│       └── config.py           # Configuration
├── uploads/                    # Uploaded files
├── scraped_data/               # Scraped job data
├── requirements.txt            # Dependencies
├── run_server.bat              # Windows batch file
├── run_server.sh               # Linux/Mac shell script
├── test_server_startup.py      # Startup verification
└── test_linkedin_scraper.py    # LinkedIn scraper tests
```

---

## 🎯 WORKFLOW

### **1. Start Server**
```bash
run_server.bat
# or
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### **2. Open API Docs**
Go to: `http://127.0.0.1:8000/docs`

### **3. Test Endpoints**
Use Swagger UI to test any endpoint

### **4. Scrape LinkedIn**
```bash
curl -X POST "http://localhost:8000/scrape-linkedin?position=Python%20Developer&work_types=Remote&max_pages=2"
```

### **5. Check Results**
```bash
ls scraped_data/
cat scraped_data/linkedin_jobs_*.csv
```

---

## ✅ FINAL CHECKLIST

- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ All services created (scraper, realtime, linkedin)
- ✅ All endpoints working
- ✅ Flair NER integrated
- ✅ Startup script created
- ✅ Tests passing

---

## 🚀 YOU'RE READY!

Your complete Job Recommendation API is ready to use with:
- ✅ Resume parsing & skill extraction
- ✅ Real-time job scraping (3 sources)
- ✅ LinkedIn job scraping with Flair skills
- ✅ Automatic job matching
- ✅ Job recommendations
- ✅ CSV + JSON export

**Start the server and go to `http://127.0.0.1:8000/docs` to try it out!** 🎉

