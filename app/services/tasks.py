import logging
import random
import time
from datetime import timedelta
from app.celery_app import celery_app
from app.services.linkedin_scraper_simple import scrape_linkedin_jobs
from app.db.supabase_db import save_jobs, archive_old_caches
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="app.services.tasks.initial_linkedin_scrape")
def initial_linkedin_scrape(self):
    """Run LinkedIn scraping and archive old caches in a Celery worker."""
    positions = [
        "Software Engineer", "Backend Developer", "Frontend Developer", "Data Scientist",
        "Full Stack Developer", "DevOps Engineer", "Machine Learning Engineer", "Data Engineer",
    ]
    locations = [
        "United States", "India", "Canada", "United Kingdom", "Germany", "Australia",
        "San Francisco", "New York", "London", "Bangalore", "Berlin", "Sydney",
    ]

    combos = [(random.choice(positions), random.choice(locations)) for _ in range(3)]
    random.shuffle(combos)

    logger.info("[Celery] Starting initial LinkedIn scrape (%d combos)", len(combos))
    for pos, loc in combos:
        delay = random.uniform(60, 120)  # throttle per target
        logger.info("[Celery] Target: %s in %s (sleep %.1fs)", pos, loc, delay)
        time.sleep(delay)
        jobs = scrape_linkedin_jobs(pos, loc, max_results=3)
        logger.info("[Celery] Scraped %d jobs for %s in %s", len(jobs or []), pos, loc)
        if jobs:
            save_jobs(jobs, pos, loc)
            logger.info("[Celery] Saved %d jobs for %s in %s", len(jobs), pos, loc)

    logger.info("[Celery] Starting archive of old cache files...")
    archived_count = archive_old_caches()
    logger.info("[Celery] Archived %d old cache files", archived_count)
    logger.info("[Celery] Completed initial LinkedIn scrape")


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Schedule daily scrape via Celery beat."""
    sender.add_periodic_task(
        timedelta(hours=24).total_seconds(),
        initial_linkedin_scrape.s(),
        name="daily_linkedin_scrape",
    )
