#!/usr/bin/env python
"""Test force_refresh parameter"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("TESTING force_refresh PARAMETER")
print("=" * 70)

# Test 1: Default (uses cache)
print("\n[Test 1] Normal request (uses cache)")
print("  URL: /scrape-jobs?keyword=python")
try:
    r = requests.post(f"{BASE_URL}/scrape-jobs?keyword=python", timeout=15)
    data = r.json()
    print(f"  Status: {r.status_code}")
    print(f"  Jobs: {data.get('jobs_count', 0)}")
    print(f"  Force Refresh: {data.get('force_refresh', 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

# Test 2: force_refresh=true (bypass cache)
print("\n[Test 2] With force_refresh=true (bypass cache)")
print("  URL: /scrape-jobs?keyword=python&force_refresh=true")
try:
    r = requests.post(f"{BASE_URL}/scrape-jobs?keyword=python&force_refresh=true", timeout=15)
    data = r.json()
    print(f"  Status: {r.status_code}")
    print(f"  Jobs: {data.get('jobs_count', 0)}")
    print(f"  Force Refresh: {data.get('force_refresh', 'N/A')}")
    if data.get('force_refresh'):
        print("  ✅ force_refresh=true is WORKING!")
    else:
        print("  ❌ force_refresh not received by API")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: force_refresh=false (explicit cache)
print("\n[Test 3] With force_refresh=false (explicit cache)")
print("  URL: /scrape-jobs?keyword=python&force_refresh=false")
try:
    r = requests.post(f"{BASE_URL}/scrape-jobs?keyword=python&force_refresh=false", timeout=15)
    data = r.json()
    print(f"  Status: {r.status_code}")
    print(f"  Jobs: {data.get('jobs_count', 0)}")
    print(f"  Force Refresh: {data.get('force_refresh', 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("If all three show correct force_refresh values, it's WORKING!")
print("=" * 70)

