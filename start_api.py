#!/usr/bin/env python
"""Start the API Server and display status"""
import subprocess
import sys
import time

print("=" * 70)
print("🚀 STARTING JOB RECOMMENDATION API SERVER")
print("=" * 70)

print("\n📌 Server Details:")
print("   Host: 0.0.0.0")
print("   Port: 8000")
print("   URL:  http://localhost:8000")

print("\n📚 API Documentation:")
print("   Swagger UI: http://localhost:8000/docs")
print("   ReDoc:      http://localhost:8000/redoc")

print("\n⏳ Starting server...\n")

try:
    # Start the server
    process = subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000"],
        cwd=r"C:\Users\rahul\PycharmProjects\PythonProject\job-scrapper"
    )
except KeyboardInterrupt:
    print("\n\n✓ Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

