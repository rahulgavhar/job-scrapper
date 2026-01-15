#!/usr/bin/env python
"""Test the file upload endpoint to verify it's working"""
import requests
import os

API_URL = "http://localhost:8000"

print("=" * 70)
print("TESTING FILE UPLOAD ENDPOINT")
print("=" * 70)

# Test 1: Health check
print("\n[Test 1] Health Check...")
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✓ Server is running")
        print(f"  Response: {response.json()}")
    else:
        print(f"✗ Health check failed: {response.status_code}")
except Exception as e:
    print(f"✗ Cannot connect to server: {e}")
    print("\nMake sure the server is running with:")
    print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    exit(1)

# Test 2: Check if sample PDF exists
print("\n[Test 2] Checking for sample PDF...")
sample_pdf = "uploads/afba3b54-43ec-4b12-b334-fd32a0f9e7b3.pdf"
if os.path.exists(sample_pdf):
    print(f"✓ Found sample PDF: {sample_pdf}")
else:
    print(f"✗ Sample PDF not found at {sample_pdf}")
    print("  You'll need to upload your own PDF file")
    sample_pdf = None

# Test 3: Test upload endpoint structure
print("\n[Test 3] Getting API documentation...")
try:
    response = requests.get(f"{API_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        upload_endpoint = openapi.get("paths", {}).get("/upload-resume", {})
        if upload_endpoint:
            print("✓ /upload-resume endpoint exists")
            post_spec = upload_endpoint.get("post", {})
            params = post_spec.get("requestBody", {}).get("content", {})
            print(f"  Accepts: {list(params.keys())}")
        else:
            print("✗ /upload-resume endpoint not found in OpenAPI spec")
    else:
        print(f"✗ Could not get OpenAPI spec: {response.status_code}")
except Exception as e:
    print(f"✗ Error getting API spec: {e}")

# Test 4: Try uploading a file (if we have one)
if sample_pdf and os.path.exists(sample_pdf):
    print(f"\n[Test 4] Testing file upload with {sample_pdf}...")
    try:
        with open(sample_pdf, 'rb') as f:
            files = {'file': ('resume.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_URL}/upload-resume", files=files)

        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.json()}")

        if response.status_code == 200:
            print("✓ File upload successful!")
        else:
            print(f"✗ Upload failed")

    except Exception as e:
        print(f"✗ Upload test failed: {e}")
else:
    print("\n[Test 4] Skipping upload test (no sample file)")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)
print("\n📝 To test manually:")
print("  1. Visit: http://localhost:8000/docs")
print("  2. Click on 'POST /upload-resume'")
print("  3. Click 'Try it out'")
print("  4. Click 'Choose File' and select a PDF")
print("  5. Click 'Execute'")
print("\n✅ The endpoint should now accept your file!")

