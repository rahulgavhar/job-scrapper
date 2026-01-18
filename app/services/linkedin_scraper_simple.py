"""
Simplified LinkedIn Job Scraper
Scrapes jobs with skills extraction and stores to Supabase
"""

import random
import time
import logging
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
JOBS_BUCKET = os.getenv("SUPABASE_JOBS_BUCKET", "job-data")
try:
    from app.services.supabase_storage import supabase_storage
except Exception:
    supabase_storage = None

# Fallback skills database for when Flair is unavailable
SKILLS_DATABASE = {
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'kotlin', 'swift', 'go', 'rust',
    'react', 'angular', 'vue', 'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'firebase',
    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github', 'jenkins', 'ci/cd',
    'html', 'css', 'scss', 'bootstrap', 'tailwind', 'webpack', 'gradle', 'maven',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark', 'kafka',
    'rest api', 'graphql', 'websocket', 'microservices', 'agile', 'scrum', 'jira',
}

USER_AGENTS = [
    # ---- Windows Chrome ----
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.58 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36",

    # ---- Windows Edge ----
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36 Edg/120.0.2210.91",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36 Edg/121.0.2277.83",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.69 Safari/537.36 Edg/122.0.2365.52",

    # ---- Windows Firefox ----
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",

    # ---- macOS Chrome ----
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.69 Safari/537.36",

    # ---- macOS Safari ----
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",

    # ---- macOS Firefox ----
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.6; rv:119.0) Gecko/20100101 Firefox/119.0",

    # ---- Linux Chrome ----
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.69 Safari/537.36",

    # ---- Linux Firefox ----
    "Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",

    # ---- Extra Variants ----
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.58 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36"
]



def extract_skills_from_text(text: str, max_skills: int = 10) -> List[str]:
    """Extract skills from text using keyword matching"""
    if not text:
        return []

    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS_DATABASE:
        if skill.lower() in text_lower:
            found_skills.append(skill.upper() if len(skill) <= 3 else skill.title())

    # Remove duplicates and return top N
    return list(dict.fromkeys(found_skills))[:max_skills]


def _get_session_with_retry() -> requests.Session:
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


def _process_job_card(
    job_element,
    position: str,
    work_type: str,
    exp_level: str,
    session: requests.Session
) -> Dict:
    """Process individual LinkedIn job card"""
    try:
        title_elem = job_element.find('h3', class_='base-search-card__title')
        company_elem = job_element.find('a', class_='hidden-nested-link')
        loc_elem = job_element.find('span', class_='job-search-card__location')
        link_elem = job_element.find('a', class_='base-card__full-link')

        if not all([title_elem, company_elem, loc_elem, link_elem]):
            return None

        title = title_elem.text.strip()
        company = company_elem.text.strip()
        location = loc_elem.text.strip()
        url = link_elem['href'].split('?')[0]

        # Fetch job description
        description = "No description available"
        skills = []

        try:
            time.sleep(random.uniform(20, 50))
            response = session.get(
                url,
                headers={
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept-Language': 'en-US,en;q=0.9'
                },
                timeout=10
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                desc_elem = soup.select_one('div.description__text') or \
                           soup.select_one('div.show-more-less-html__markup')

                if desc_elem:
                    description = desc_elem.get_text('\n').strip()[:2000]
                    skills = extract_skills_from_text(description)

        except Exception as e:
            logger.warning(f"Failed to fetch description for {url}: {e}")

        return {
            "position": position,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "work_type": work_type,
            "experience_level": exp_level,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "description": description,
            "skills": ", ".join(skills) if skills else "No skills found",
            "source": "LinkedIn"
        }

    except Exception as e:
        logger.error(f"Error processing job: {e}")
        return None


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_") or "na"


def _cache_jobs_to_supabase(position: str, location: str, jobs: List[Dict]):
    """Deprecated local cache uploader. Use app.db.supabase_db.save_jobs instead."""
    try:
        from app.db.supabase_db import save_jobs
        save_jobs(jobs, position, location)
    except Exception as e:
        logger.error("Failed to store jobs via DB module: %s", e)


def scrape_linkedin_jobs(
    position: str,
    location: str,
    max_results: int = 50
) -> List[Dict]:
    """
    Scrape LinkedIn jobs for a specific position and location

    Args:
        position: Job title/position
        location: Job location
        max_results: Maximum jobs to scrape

    Returns:
        List of job dictionaries with extracted skills
    """

    logger.info(f"🔗 Starting LinkedIn scrape: {position} in {location}")

    session = _get_session_with_retry()
    all_jobs = []

    work_types = ["Remote", "Hybrid", "On-site"]
    exp_levels = ["Entry level", "Associate", "Mid-Senior level"]

    work_type_map = {
        "On-site": "f_WT=1",
        "Hybrid": "f_WT=2",
        "Remote": "f_WT=3"
    }

    exp_level_map = {
        "Internship": "f_E=1",
        "Entry level": "f_E=2",
        "Associate": "f_E=3",
        "Mid-Senior level": "f_E=4"
    }

    for work_type in work_types:
        for exp_level in exp_levels:
            if len(all_jobs) >= max_results:
                logger.info(f"✓ Reached max results: {max_results}")
                _cache_jobs_to_supabase(position, location, all_jobs)
                return all_jobs

            try:
                base_url = (
                    f"https://www.linkedin.com/jobs/search/?"
                    f"keywords={position.replace(' ', '%20')}"
                    f"&location={location.replace(' ', '%20')}"
                    f"&{work_type_map.get(work_type, '')}"
                    f"&{exp_level_map.get(exp_level, '')}"
                    f"&radius=0"
                )

                # Fetch jobs page
                response = session.get(base_url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')

                if not job_cards:
                    logger.info(f"No jobs found for {work_type}, {exp_level}")
                    continue

                for job_card in job_cards:
                    if len(all_jobs) >= max_results:
                        break

                    # Slow down between job card fetches
                    time.sleep(random.uniform(10.0, 20.5))

                    job_data = _process_job_card(
                        job_card,
                        position,
                        work_type,
                        exp_level,
                        session
                    )

                    if job_data:
                        all_jobs.append(job_data)
                        logger.info(f"✓ Scraped: {job_data['title']} at {job_data['company']}")

                # Extra throttle per batch of job cards
                time.sleep(random.uniform(20, 40))

                time.sleep(random.uniform(3, 7))

            except Exception as e:
                logger.error(f"Error scraping {work_type}, {exp_level}: {e}")
                continue

    logger.info(f"✓ Scraping complete. Total jobs: {len(all_jobs)}")
    _cache_jobs_to_supabase(position, location, all_jobs)
    return all_jobs

