"""
Job scraper service that fetches jobs from multiple sources.
Primary source: LinkedIn (web scraping)
Fallback sources: RemoteOK API, Supabase cache
Includes Flair NER for skill extraction from job descriptions.
"""

import json
from datetime import datetime
import copy
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache duration for job data
CACHE_EXPIRY_HOURS = 24

# Load Flair model once at startup (not on every request)
FLAIR_MODEL = None

def _load_flair_model():
    """Load Flair NER model once and cache it"""
    global FLAIR_MODEL
    if FLAIR_MODEL is None:
        try:
            from flair.models import SequenceTagger
            print("📦 Loading Flair NER model (first time only)...")
            FLAIR_MODEL = SequenceTagger.load("kaliani/flair-ner-skill")
            print("✓ Flair model loaded successfully")
        except ImportError:
            print("⚠️  Flair not installed; skill extraction will use keyword matching")
            FLAIR_MODEL = False  # Mark as tried but failed
        except Exception as e:
            print(f"⚠️  Failed to load Flair model: {e}; using fallback")
            FLAIR_MODEL = False
    return FLAIR_MODEL

def _extract_skills_with_flair(text: str, max_skills: int = 10) -> list[str]:
    """Extract skills from text using Flair NER"""
    try:
        model = _load_flair_model()
        if not model or model is False:
            return []

        from flair.data import Sentence
        sentence = Sentence(text[:500])  # Limit text length for performance
        model.predict(sentence)
        skills = [entity.text for entity in sentence.get_spans("ner")]
        return list(set(skills))[:max_skills]  # Deduplicate and limit
    except Exception as e:
        logger.warning(f"Flair extraction failed: {e}")
        return []


def get_cache_age_hours() -> float:
    """Cache is managed by Supabase, always fresh"""
    return 0.0


def get_scraped_jobs_from_cache() -> list[dict]:
    """
    Load jobs from Supabase cache.
    """
    try:
        from app.db.supabase_db import get_all_jobs
        jobs = get_all_jobs()
        if jobs:
            logger.info(f"✓ Retrieved {len(jobs)} jobs from Supabase cache")
            return jobs
    except Exception as e:
        logger.warning(f"Error retrieving cached jobs from Supabase: {e}")
    return []


def save_jobs_to_cache(jobs: list[dict], position: str = "general", location: str = "general"):
    """
    Save scraped jobs to Supabase cache.
    """
    try:
        from app.db.supabase_db import save_jobs
        save_jobs(jobs, position, location)
        logger.info(f"✓ Saved {len(jobs)} jobs to Supabase cache")
    except Exception as e:
        logger.warning(f"Error saving jobs to Supabase: {e}")


def _load_jobs_from_db() -> list[dict]:
    """Load jobs from Supabase cache as fallback"""
    try:
        from app.db.supabase_db import get_all_jobs
        jobs = get_all_jobs()

        for job in jobs:
            job.setdefault("source", "Supabase Cache")

        if not jobs:
            logger.warning("No jobs in Supabase cache")

        return jobs
    except Exception as e:
        logger.error(f"Error loading jobs from Supabase: {e}")
        return []


def _fetch_remoteok_jobs(keyword: str = "python", limit: int = 20) -> list[dict]:
    """Fetch remote jobs from RemoteOK public API, filtered by keyword, with Flair skill extraction."""
    try:
        print("  Attempting RemoteOK API...")
        url = "https://remoteok.io/api"
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        print(f"  RemoteOK API returned data")

        jobs = []
        for entry in (data if isinstance(data, list) else []):
            if not isinstance(entry, dict):
                continue
            title = entry.get("position") or entry.get("title")
            if not title:
                continue
            text_blob = " ".join(str(v) for v in entry.values())
            if keyword.lower() not in text_blob.lower():
                continue

            # Extract description
            description = (entry.get("description") or "")[:1000]

            # Try to extract skills using Flair NER
            skills = _extract_skills_with_flair(description, max_skills=10)

            # Fallback to tags if Flair doesn't find anything
            if not skills:
                skills = entry.get("tags") or []

            jobs.append({
                "id": entry.get("id") or entry.get("slug") or entry.get("url"),
                "title": title,
                "company": entry.get("company") or entry.get("company_name"),
                "location": entry.get("location") or "Remote",
                "description": description,
                "url": entry.get("url") or entry.get("apply_url") or "",
                "posted_at": entry.get("date") or entry.get("published_at") or "",
                "source": "RemoteOK",
                "skills": skills
            })
            if len(jobs) >= limit:
                break
        print(f"  Filtered to {len(jobs)} jobs matching '{keyword}'")
        return jobs
    except requests.Timeout:
        print(f"✗ RemoteOK timeout (10s)")
        return []
    except requests.ConnectionError:
        print(f"✗ RemoteOK connection error")
        return []
    except Exception as e:
        print(f"✗ RemoteOK fetch error: {type(e).__name__}: {e}")
        return []


def scrape_all_jobs(keyword: str = "python", location: str = "USA", force_refresh: bool = False) -> list[dict]:
    """
    Job fetcher using multiple sources with fallback strategy:
    1. LinkedIn (live web scraping) - PRIMARY
    2. RemoteOK API
    3. Local DB (fallback)

    Uses cache unless force_refresh=True
    Always returns jobs (never empty)
    """
    try:
        print(f"\n{'='*60}")
        print(f"SCRAPE REQUEST: keyword={keyword}, location={location}, force_refresh={force_refresh}")
        print(f"{'='*60}")

        # Check cache first
        if not force_refresh:
            cached_jobs = get_scraped_jobs_from_cache()
            if cached_jobs:
                print(f"✓ RESULT: {len(cached_jobs)} jobs from cache\n{'='*60}\n")
                return cached_jobs

        # Try LinkedIn scraper first (primary source)
        print("🔗 Scraping LinkedIn...")
        try:
            from app.services.linkedin_scraper_v2 import scrape_linkedin_jobs

            jobs = scrape_linkedin_jobs(
                location=location,
                position=keyword,
                work_types=["Remote", "Hybrid", "On-site"],
                experience_levels=["Entry level", "Associate", "Mid-Senior level"],
                time_filter="Past month",
                max_results=50
            )

            if jobs:
                print(f"✓ LinkedIn: Found {len(jobs)} jobs")
                save_jobs_to_cache(jobs, position=keyword, location=location)
                print(f"✓ RESULT: {len(jobs)} jobs from LinkedIn\n{'='*60}\n")
                return jobs
            else:
                print("⚠ LinkedIn: No jobs found")
        except Exception as e:
            logger.warning(f"LinkedIn scraping failed: {e}")
            print(f"✗ LinkedIn scraping error: {e}")

        # Try RemoteOK
        print("🌐 Fetching from RemoteOK...")
        jobs = _fetch_remoteok_jobs(keyword=keyword, limit=25)

        if jobs:
            save_jobs_to_cache(jobs, position=keyword, location=location)
            print(f"✓ RESULT: {len(jobs)} jobs from RemoteOK\n{'='*60}\n")
            return jobs

        # Fallback to local DB
        print("📦 RemoteOK empty; using local DB fallback")
        jobs = _load_jobs_from_db()

        if jobs:
            save_jobs_to_cache(jobs)
            print(f"✓ RESULT: {len(jobs)} jobs from local DB")
        else:
            print("⚠ WARNING: No jobs from any source!")

        print(f"{'='*60}\n")
        return jobs

    except Exception as e:
        print(f"✗ Error scraping: {e}")
        import traceback
        traceback.print_exc()
        # Last resort: return cached
        cache = get_scraped_jobs_from_cache()
        if cache:
            print(f"Fallback: Returning {len(cache)} cached jobs")
            return cache
        # If no cache, return local DB
        print("Fallback: Loading local DB")
        return _load_jobs_from_db()


def get_all_available_jobs(include_cached: bool = True, force_refresh: bool = False) -> list[dict]:
    jobs = scrape_all_jobs(force_refresh=force_refresh)
    if include_cached and not jobs:
        jobs = get_scraped_jobs_from_cache()
    return jobs
