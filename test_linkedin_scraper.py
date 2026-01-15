#!/usr/bin/env python
"""
Test LinkedIn Scraper
Verify all functionality works correctly
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
SCRAPE_URL = f"{BASE_URL}/scrape-linkedin"

def test_linkedin_scraper():
    """Test LinkedIn scraper endpoint"""
    print("\n" + "="*70)
    print("LINKEDIN SCRAPER TEST")
    print("="*70 + "\n")

    # Test 1: Health check
    print("✓ Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        print(f"  ✅ Server is running\n")
    except Exception as e:
        print(f"  ❌ Server not responding: {e}\n")
        return

    # Test 2: Scrape with minimal parameters
    print("✓ Test 2: Scrape Python Developer (Minimal)")
    try:
        print("  Sending request...")
        response = requests.post(
            SCRAPE_URL + "?position=Python+Developer&max_pages=1",
            timeout=300  # 5 minutes timeout for scraping
        )

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            jobs_count = data.get('jobs_count', 0)
            print(f"  ✅ Jobs scraped: {jobs_count}")
            print(f"  Files: CSV={data.get('files', {}).get('csv')}")
            print(f"         JSON={data.get('files', {}).get('json')}\n")
        else:
            print(f"  ❌ Error: {response.text}\n")

    except requests.Timeout:
        print(f"  ⚠️  Request timeout (scraping takes time)\n")
    except Exception as e:
        print(f"  ❌ Error: {e}\n")

    # Test 3: Scrape with multiple filters
    print("✓ Test 3: Scrape with Multiple Filters")
    try:
        print("  Sending request...")
        response = requests.post(
            SCRAPE_URL + "?position=Data+Scientist&location=San+Francisco&work_types=Remote,Hybrid&max_pages=1",
            timeout=300
        )

        if response.status_code == 200:
            data = response.json()
            jobs_count = data.get('jobs_count', 0)
            print(f"  ✅ Jobs scraped: {jobs_count}")

            # Show first job
            if data.get('jobs') and len(data['jobs']) > 0:
                job = data['jobs'][0]
                print(f"  First job:")
                print(f"    Title: {job.get('Title')}")
                print(f"    Company: {job.get('Company')}")
                print(f"    Skills: {job.get('Skills')}\n")
        else:
            print(f"  ❌ Error: {response.text}\n")

    except requests.Timeout:
        print(f"  ⚠️  Request timeout (scraping takes time)\n")
    except Exception as e:
        print(f"  ❌ Error: {e}\n")

    # Test 4: Check saved files
    print("✓ Test 4: Check Saved Files")
    try:
        data_dir = Path("scraped_data")
        if data_dir.exists():
            csv_files = list(data_dir.glob("*linkedin*.csv"))
            json_files = list(data_dir.glob("*linkedin*.json"))

            print(f"  CSV files: {len(csv_files)}")
            if csv_files:
                latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
                print(f"    Latest: {latest_csv.name} ({latest_csv.stat().st_size} bytes)")

            print(f"  JSON files: {len(json_files)}")
            if json_files:
                latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
                print(f"    Latest: {latest_json.name} ({latest_json.stat().st_size} bytes)")

            if csv_files or json_files:
                print(f"  ✅ Files saved successfully\n")
            else:
                print(f"  ⚠️  No saved files found\n")
        else:
            print(f"  ⚠️  scraped_data directory not found\n")

    except Exception as e:
        print(f"  ❌ Error checking files: {e}\n")

    print("="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("\n⚠️  Make sure server is running: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    input("Press Enter to start tests...")
    test_linkedin_scraper()

