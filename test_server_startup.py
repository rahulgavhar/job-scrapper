#!/usr/bin/env python
"""
Test script to verify server starts correctly
"""
import sys
import traceback

print("\n" + "="*70)
print("SERVER STARTUP TEST")
print("="*70 + "\n")

# Test 1: Import app
print("✓ Test 1: Import FastAPI app")
try:
    from app.main import app
    print("  ✅ App imported successfully\n")
except Exception as e:
    print(f"  ❌ Failed to import app: {e}\n")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check routes
print("✓ Test 2: Check API routes")
try:
    routes = [route.path for route in app.routes]
    print(f"  ✅ Found {len(routes)} routes")
    for route in routes[:5]:
        print(f"     - {route}")
    print()
except Exception as e:
    print(f"  ❌ Failed to check routes: {e}\n")
    sys.exit(1)

# Test 3: Verify dependencies
print("✓ Test 3: Verify dependencies")
try:
    import requests
    import pandas
    import bs4
    print("  ✅ requests: installed")
    print("  ✅ pandas: installed")
    print("  ✅ beautifulsoup4: installed")
    print()
except Exception as e:
    print(f"  ❌ Missing dependency: {e}\n")
    sys.exit(1)

# Test 4: Flair (optional)
print("✓ Test 4: Check Flair (optional)")
try:
    from flair.models import SequenceTagger
    print("  ✅ Flair installed\n")
except ImportError:
    print("  ⚠️  Flair not installed (optional)\n")
except Exception as e:
    print(f"  ⚠️  Flair error: {e}\n")

print("="*70)
print("✅ ALL TESTS PASSED - SERVER READY!")
print("="*70)
print("\nRun server with:")
print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload\n")

