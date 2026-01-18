"""
Supabase Jobs Database - Stores and retrieves jobs from Supabase storage
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict

logger = logging.getLogger(__name__)

# Use SUPABASE_JOBS_BUCKET from .env, fallback to job-data
JOBS_BUCKET = os.getenv("SUPABASE_JOBS_BUCKET", "job-data")
CACHE_DURATION_HOURS = 24
ARCHIVE_AGE_DAYS = 7

logger.info(f"Using jobs bucket: {JOBS_BUCKET}")


def _get_supabase_client():
    """Get Supabase client from the shared storage service"""
    try:
        from app.services.supabase_storage import supabase_storage
        if supabase_storage and supabase_storage.client:
            return supabase_storage.client
    except Exception:
        pass
    return None


def _ensure_bucket_exists() -> bool:
    """
    Verify the target bucket exists and is accessible with the current key.
    Note: Anon keys cannot create buckets. Expect buckets to be pre-created.
    """
    client = _get_supabase_client()
    if not client:
        logger.error("Supabase client not available")
        return False
    try:
        # Listing the root of the bucket verifies it exists and is accessible.
        client.storage.from_(JOBS_BUCKET).list()
        return True
    except Exception as e:
        logger.error(f"Bucket '{JOBS_BUCKET}' not accessible: {e}")
        return False


def save_jobs(jobs: List[Dict], position: str, location: str) -> bool:
    """Save jobs to Supabase cache under job-data bucket."""
    if not _ensure_bucket_exists():
        logger.error("Cannot ensure bucket exists; aborting save")
        return False

    client = _get_supabase_client()
    if not client:
        logger.error("Supabase not initialized")
        return False

    cache_key = f"jobs_{position.lower().replace(' ', '_')}_{location.lower().replace(' ', '_')}"
    file_path = f"jobs/cache/{cache_key}.json"

    data = {
        "position": position,
        "location": location,
        "total_jobs": len(jobs),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "cache_expires_at": (datetime.now(timezone.utc) + timedelta(hours=CACHE_DURATION_HOURS)).isoformat(),
        "jobs": jobs,
    }

    try:
        # Prepare JSON content as raw bytes (Supabase client expects bytes, not file objects)
        json_content = json.dumps(data).encode("utf-8")

        # Upload to Supabase with explicit headers
        response = client.storage.from_(JOBS_BUCKET).upload(
            file_path,
            json_content,
            {
                "cacheControl": "3600",
                "upsert": "true",
                "contentType": "application/json"
            }
        )

        # Treat None or empty dict as success (client libraries differ)
        if not response or (isinstance(response, dict) and not response.get("error")):
            logger.info(f"✓ Saved {len(jobs)} jobs to Supabase at {file_path}")
            return True

        if hasattr(response, "error") and response.error:
            logger.error(f"Upload error: {response.error}")
            return False

        logger.info(f"✓ Saved {len(jobs)} jobs to Supabase at {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving jobs: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_cached_jobs(position: str = "", location: str = "") -> List[Dict]:
    """
    Retrieve cached jobs from Supabase if available.
    If position/location are given, tries to read the specific cache file.
    Otherwise, lists cache folder and aggregates jobs.
    """
    client = _get_supabase_client()
    if not client:
        return []
    if not _ensure_bucket_exists():
        return []

    try:
        jobs_out: List[Dict] = []
        if position and location:
            cache_key = f"jobs_{position.lower().replace(' ', '_')}_{location.lower().replace(' ', '_')}"
            file_path = f"jobs/cache/{cache_key}.json"
            try:
                content = client.storage.from_(JOBS_BUCKET).download(file_path)
                data = json.loads(content.decode("utf-8")) if isinstance(content, (bytes, bytearray)) else json.loads(content)
                jobs_out.extend(data.get("jobs", []))
                return jobs_out
            except Exception:
                # Fall through to listing all cache files
                pass

        # List all cached files and aggregate
        entries = client.storage.from_(JOBS_BUCKET).list("jobs/cache")
        for entry in entries or []:
            name = entry.get("name") if isinstance(entry, dict) else getattr(entry, "name", None)
            if not name or not name.endswith(".json"):
                continue
            try:
                content = client.storage.from_(JOBS_BUCKET).download(f"jobs/cache/{name}")
                data = json.loads(content.decode("utf-8")) if isinstance(content, (bytes, bytearray)) else json.loads(content)
                jobs_out.extend(data.get("jobs", []))
            except Exception:
                continue
        return jobs_out
    except Exception as e:
        logger.error(f"Error reading cached jobs: {e}")
        return []


def archive_old_caches() -> int:
    """Move cache files older than ARCHIVE_AGE_DAYS to jobs/archived.
    Returns number of archived files.
    """
    client = _get_supabase_client()
    if not client or not _ensure_bucket_exists():
        return 0

    archived_count = 0
    try:
        entries = client.storage.from_(JOBS_BUCKET).list("jobs/cache") or []
        now = datetime.now(timezone.utc)
        for entry in entries:
            name = entry.get("name") if isinstance(entry, dict) else getattr(entry, "name", None)
            if not name or not name.endswith(".json"):
                continue
            # Download and inspect scraped_at
            try:
                raw = client.storage.from_(JOBS_BUCKET).download(f"jobs/cache/{name}")
                data = json.loads(raw.decode("utf-8")) if isinstance(raw, (bytes, bytearray)) else json.loads(raw)
                scraped_at = data.get("scraped_at")
                if not scraped_at:
                    continue
                try:
                    scraped_dt = datetime.fromisoformat(scraped_at.replace("Z", "+00:00"))
                except Exception:
                    continue
                if (now - scraped_dt) >= timedelta(days=ARCHIVE_AGE_DAYS):
                    # Move: upload to archived then remove original
                    archived_path = f"jobs/archived/{name}"
                    payload = json.dumps(data).encode("utf-8")
                    res_up = client.storage.from_(JOBS_BUCKET).upload(
                        archived_path,
                        payload,
                        {"contentType": "application/json", "upsert": "true"}
                    )
                    if not res_up or (isinstance(res_up, dict) and not res_up.get("error")):
                        client.storage.from_(JOBS_BUCKET).remove([f"jobs/cache/{name}"])
                        archived_count += 1
            except Exception:
                continue
        return archived_count
    except Exception as e:
        logger.error(f"Error archiving caches: {e}")
        return 0
