# 📮 POSTMAN API TESTING GUIDE

## ✅ API IS COMPLETELY STATELESS - POSTMAN WORKS PERFECTLY!

**Your concern about stateless APIs is GOOD NEWS for Postman!** 

Stateless means:
- ✅ No sessions to manage
- ✅ No cookies required
- ✅ No login needed
- ✅ Each request is independent
- ✅ Perfect for Postman testing!

---

## 🚀 QUICK START WITH POSTMAN

### **Method 1: Import the Collection (EASIEST)**

1. **Open Postman**

2. **Click "Import"** (top left)

3. **Select File**: `Postman_Collection.json` from the project folder

4. **Done!** All endpoints are ready to test

### **Method 2: Manual Setup**

Follow the instructions below to test each endpoint manually.

---

## 📝 TESTING EACH ENDPOINT

### **1. Health Check**
✅ Simple GET request - No authentication needed

**Request:**
```
GET http://localhost:8000/health
```

**Postman Steps:**
1. New Request → GET
2. URL: `http://localhost:8000/health`
3. Click "Send"

**Expected Response:**
```json
{
  "status": "ok",
  "service": "Job Recommendation API",
  "version": "1.0.0"
}
```

---

### **2. Upload Resume & Get Recommendations** 
✅ Main endpoint - File upload

**Request:**
```
POST http://localhost:8000/upload-resume
```

**Postman Steps:**
1. New Request → POST
2. URL: `http://localhost:8000/upload-resume`
3. Go to **Body** tab
4. Select **form-data**
5. Add field:
   - Key: `file` (change type to "File" from dropdown)
   - Value: Click "Select Files" and choose a PDF
6. Click "Send"

**Expected Response:**
```json
{
  "success": true,
  "message": "Resume processed successfully",
  "file_name": "resume.pdf",
  "skills": ["Python", "Django", "FastAPI", "REST API"],
  "recommendations": [
    {
      "id": 1,
      "title": "Software Engineer",
      "company": "TechCorp",
      "match_score": 0.95,
      "matched_skills": ["Python", "Django"]
    }
  ]
}
```

---

### **3. Recommend by Skills (NO FILE NEEDED!)**
✅ Stateless endpoint - Just send JSON

**Request:**
```
POST http://localhost:8000/recommend-by-skills
```

**Postman Steps:**
1. New Request → POST
2. URL: `http://localhost:8000/recommend-by-skills`
3. Go to **Body** tab
4. Select **raw**
5. Change format to **JSON**
6. Paste this:
```json
{
  "skills": ["Python", "Django", "FastAPI", "REST API"],
  "top_n": 5
}
```
7. Click "Send"

**Expected Response:**
```json
{
  "success": true,
  "skills": ["Python", "Django", "FastAPI", "REST API"],
  "recommendations": [...]
}
```

---

### **4. List All Jobs**
✅ Simple GET request with query parameters

**Request:**
```
GET http://localhost:8000/jobs?skip=0&limit=10
```

**Postman Steps:**
1. New Request → GET
2. URL: `http://localhost:8000/jobs`
3. Go to **Params** tab
4. Add parameters:
   - `skip`: 0
   - `limit`: 10
5. Click "Send"

**Expected Response:**
```json
{
  "success": true,
  "total_jobs": 8,
  "returned_jobs": 8,
  "jobs": [...]
}
```

---

### **5. Analyze Resume (Skills Only)**
✅ Extract skills without job matching

**Request:**
```
POST http://localhost:8000/analyze-resume
```

**Postman Steps:**
1. New Request → POST
2. URL: `http://localhost:8000/analyze-resume`
3. Body → form-data
4. Add field:
   - Key: `file` (File type)
   - Value: Select PDF
5. Click "Send"

**Expected Response:**
```json
{
  "success": true,
  "extracted_skills": ["Python", "Django", "FastAPI"],
  "skills_count": 3,
  "recommendations": [],
  "recommendations_count": 0
}
```

---

## 🔧 POSTMAN TIPS

### **Setting Base URL as Variable**

1. Click "Environments" → "Create Environment"
2. Name: `Job API Local`
3. Add variable:
   - Variable: `baseUrl`
   - Initial Value: `http://localhost:8000`
   - Current Value: `http://localhost:8000`
4. Save
5. Use in requests: `{{baseUrl}}/upload-resume`

### **File Upload Tips**

- Make sure file key is exactly `file` (lowercase)
- Change type from "Text" to "File" in dropdown
- Only PDF files are accepted
- File is uploaded fresh with each request (stateless!)

### **Common Headers (NOT NEEDED)**

Good news! These are NOT required:
- ❌ No Authorization header needed
- ❌ No API key needed
- ❌ No session cookie needed
- ❌ No CSRF token needed

Only for JSON requests:
- ✅ Content-Type: application/json (Postman adds automatically)

---

## 🎯 TESTING WORKFLOW

### **Basic Test Flow:**
```
1. Health Check (GET /health)
   ↓
2. List Jobs (GET /jobs)
   ↓
3. Upload Resume (POST /upload-resume)
   ↓
4. Review recommendations
```

### **Skills-Based Test Flow (No File):**
```
1. Health Check (GET /health)
   ↓
2. Recommend by Skills (POST /recommend-by-skills)
   ↓
3. Get specific job details
```

---

## 📊 ALL ENDPOINTS SUMMARY

| Endpoint | Method | Body Type | Auth | Stateless |
|----------|--------|-----------|------|-----------|
| `/health` | GET | None | No | ✅ |
| `/` | GET | None | No | ✅ |
| `/ping` | GET | None | No | ✅ |
| `/upload-resume` | POST | form-data | No | ✅ |
| `/analyze-resume` | POST | form-data | No | ✅ |
| `/get-recommendations` | POST | form-data | No | ✅ |
| `/recommend-by-skills` | POST | JSON | No | ✅ |
| `/jobs` | GET | None | No | ✅ |
| `/scrape-jobs` | POST | None | No | ✅ |

**ALL ENDPOINTS ARE STATELESS ✅**

---

## 🐛 TROUBLESHOOTING

### **"Field required" error**
✅ **FIXED!** Make sure:
- Key name is exactly `file` (lowercase)
- Type is set to "File" not "Text"
- A PDF file is selected

### **Connection refused**
```
Check server is running:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### **"Only PDF files are accepted"**
- Make sure file has `.pdf` extension
- File type validation is working correctly

### **Empty response**
- Check Postman Console (View → Show Postman Console)
- Verify server logs

---

## 💡 EXAMPLE TEST SCRIPT

Save this as a Postman test:

```javascript
// Test for /upload-resume
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('success');
    pm.expect(jsonData.success).to.be.true;
});

pm.test("Skills are extracted", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.skills).to.be.an('array');
    pm.expect(jsonData.skills.length).to.be.above(0);
});

pm.test("Recommendations returned", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.recommendations).to.be.an('array');
});
```

---

## ✅ WHY POSTMAN WORKS PERFECTLY

1. **Stateless Design**: Each request is independent
2. **No Sessions**: No cookies or session management needed
3. **No Authentication**: Open API for testing
4. **File Upload**: Standard multipart/form-data (Postman supports this)
5. **JSON Responses**: Easy to read and test
6. **REST Principles**: Follows REST best practices

---

## 🚀 READY TO TEST!

1. ✅ Server is running: `http://localhost:8000`
2. ✅ Import collection: `Postman_Collection.json`
3. ✅ Start testing!

**The API is 100% compatible with Postman!** 🎉

No state management, no sessions, no cookies - just clean, stateless HTTP requests!

