"""
Job scraper service that fetches jobs from multiple sources.
Uses RemoteOK API with local DB fallback.
Includes Flair NER for skill extraction from job descriptions.
"""

import json
from datetime import datetime
from pathlib import Path
import copy
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache file for scraped jobs
CACHE_FILE = Path("uploads/jobs_cache.json")
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
    """Get age of cache file in hours"""
    if CACHE_FILE.exists():
        cache_time = CACHE_FILE.stat().st_mtime
        current_time = datetime.now().timestamp()
        return (current_time - cache_time) / 3600
    return float('inf')


def get_scraped_jobs_from_cache() -> list[dict]:
    """
    Load jobs from cache file if it exists and is fresh.
    """
    if CACHE_FILE.exists():
        cache_age = get_cache_age_hours()
        if cache_age < CACHE_EXPIRY_HOURS:
            try:
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get("jobs"):
                        print(f"✓ Using cached jobs (age: {cache_age:.1f} hours, {len(data.get('jobs', []))} jobs)")
                        return data["jobs"]
            except Exception as e:
                print(f"Error loading job cache: {e}")
    return []


def save_jobs_to_cache(jobs: list[dict]):
    """
    Save scraped jobs to cache file.
    """
    try:
        CACHE_FILE.parent.mkdir(exist_ok=True)
        data = {
            "jobs": jobs,
            "cached_at": datetime.now().isoformat(),
            "total_jobs": len(jobs),
            "sources": list(set(j.get('source', 'Unknown') for j in jobs))
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Saved {len(jobs)} jobs to cache from sources: {data['sources']}")
    except Exception as e:
        print(f"Error saving job cache: {e}")


def _load_jobs_from_db() -> list[dict]:
    """Load sample jobs from local DB and extract skills using Flair"""
    from app.db.fake_db import get_all_jobs as get_db_jobs
    # work on a copy to avoid mutating the global DB
    jobs = copy.deepcopy(get_db_jobs())
    for job in jobs:
        job.setdefault("source", "Sample DB")
        job.setdefault("url", "")
        job.setdefault("posted_at", datetime.now().date().isoformat())

        # Extract skills from description using Flair
        description = job.get("description", "")
        if description and not job.get("skills"):
            skills = _extract_skills_with_flair(description, max_skills=10)
            if skills:
                job["skills"] = skills
            else:
                job["skills"] = job.get("skills", [])
        else:
            job.setdefault("skills", [])
    return jobs


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
    Job fetcher using RemoteOK (live) with local DB fallback.
    - Uses cache unless force_refresh=True
    - Tries RemoteOK first; if empty, falls back to local DB
    - Always returns jobs (never empty)
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

        # Try RemoteOK
        print("🌐 Fetching from RemoteOK...")
        jobs = _fetch_remoteok_jobs(keyword=keyword, limit=25)

        # Fallback to local DB
        if not jobs:
            print("📦 RemoteOK empty; using local DB fallback")
            jobs = _load_jobs_from_db()

        # Save to cache
        if jobs:
            save_jobs_to_cache(jobs)
            print(f"✓ RESULT: {len(jobs)} jobs")
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
