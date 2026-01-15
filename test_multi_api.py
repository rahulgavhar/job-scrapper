#!/usr/bin/env python
"""Test the multi-API job scraper with detailed logging"""
import asyncio
import time

async def test_scraper():
    print("=" * 70)
    print("TESTING MULTI-API JOB SCRAPER")
    print("=" * 70)

    start = time.time()

    try:
        from app.services.job_api_fetcher import JobAPIFetcher

        print("\n📌 Testing GitHub Jobs API...")
        fetcher = JobAPIFetcher()

        # Test individual APIs
        await fetcher.init_session()

        print("  Fetching from GitHub Jobs...")
        github_jobs = await fetcher.fetch_github_jobs("python")
        print(f"  ✓ GitHub Jobs: {len(github_jobs)} jobs")

        print("  Fetching from Jooble...")
        jooble_jobs = await fetcher.fetch_jooble_jobs("python", "USA")
        print(f"  ✓ Jooble: {len(jooble_jobs)} jobs")

        print("  Fetching from Adzuna...")
        adzuna_jobs = await fetcher.fetch_adzuna_jobs("python", "United States")
        print(f"  ✓ Adzuna: {len(adzuna_jobs)} jobs")

        print("  Fetching from RemoteOK...")
        remote_jobs = await fetcher.fetch_remoteok_jobs("python")
        print(f"  ✓ RemoteOK: {len(remote_jobs)} jobs")

        print("  Fetching from Working Nomads...")
        nomads_jobs = await fetcher.fetch_workingnomads_jobs()
        print(f"  ✓ Working Nomads: {len(nomads_jobs)} jobs")

        print("  Fetching from Stack Overflow...")
        so_jobs = await fetcher.fetch_stackoverflow_jobs("python", "US")
        print(f"  ✓ Stack Overflow: {len(so_jobs)} jobs")

        await fetcher.close_session()

        total_jobs = len(github_jobs) + len(jooble_jobs) + len(adzuna_jobs) + len(remote_jobs) + len(nomads_jobs) + len(so_jobs)
        elapsed = time.time() - start

        print(f"\n{'=' * 70}")
        print(f"RESULTS:")
        print(f"  Total jobs: {total_jobs}")
        print(f"  Time taken: {elapsed:.2f} seconds")
        print(f"{'=' * 70}\n")

        if total_jobs > 0:
            print("✅ SUCCESS: Jobs are being fetched from multiple APIs!")
        else:
            print("⚠️  WARNING: No jobs fetched, APIs may be down or rate-limited")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())

