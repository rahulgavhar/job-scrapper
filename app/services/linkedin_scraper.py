"""
LinkedIn Job Scraper with Flair NER Skill Extraction
Scrapes real jobs from LinkedIn and extracts skills using Flair
"""

import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
import threading
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directories
DATA_DIR = Path("scraped_data")
DATA_DIR.mkdir(exist_ok=True)

# Load Flair model once at startup
FLAIR_MODEL = None

def _load_flair_model():
    """Load Flair NER model once and cache it"""
    global FLAIR_MODEL
    if FLAIR_MODEL is None:
        try:
            from flair.models import SequenceTagger
            logger.info("📦 Loading Flair NER model...")
            FLAIR_MODEL = SequenceTagger.load("kaliani/flair-ner-skill")
            logger.info("✓ Flair model loaded")
        except ImportError:
            logger.warning("⚠️ Flair not installed; install with: pip install flair")
            FLAIR_MODEL = False
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Flair: {e}")
            FLAIR_MODEL = False
    return FLAIR_MODEL

def get_skills(text: str, max_skills: int = 5) -> List[str]:
    """Extract skills from text using Flair NER"""
    try:
        model = _load_flair_model()
        if not model or model is False:
            return []

        from flair.data import Sentence
        sentence = Sentence(text[:500])
        model.predict(sentence)
        skills = [entity.text for entity in sentence.get_spans("ner")]
        return list(set(skills))[:max_skills]
    except Exception as e:
        logger.debug(f"Skill extraction failed: {e}")
        return []

# LinkedIn URL mappings
experience_level_mapping = {
    "Internship": "f_E=1",
    "Entry level": "f_E=2",
    "Associate": "f_E=3",
    "Mid-Senior level": "f_E=4"
}

work_type_mapping = {
    "On-site": "f_WT=1",
    "Hybrid": "f_WT=2",
    "Remote": "f_WT=3"
}

time_filter_mapping = {
    "Past 24 hours": "f_TPR=r86400",
    "Past week": "f_TPR=r604800",
    "Past month": "f_TPR=r2592000",
}

class LinkedInScraperManager:
    """Manages LinkedIn job scraping with thread safety"""

    def __init__(self):
        self.stop_event = threading.Event()
        self.current_df = pd.DataFrame()
        self.lock = threading.Lock()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def reset(self):
        """Reset scraper state"""
        self.stop_event.clear()
        self.current_df = pd.DataFrame()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_job(self, job_data: Dict):
        """Thread-safe job addition"""
        with self.lock:
            new_df = pd.DataFrame([job_data])
            self.current_df = pd.concat([self.current_df, new_df], ignore_index=True)

    def save_csv(self, filename: Optional[str] = None) -> str:
        """Save scraped jobs to CSV"""
        try:
            DATA_DIR.mkdir(exist_ok=True)

            if filename is None:
                filename = f"linkedin_jobs_{self.timestamp}.csv"

            filepath = DATA_DIR / filename

            with self.lock:
                if self.current_df.empty:
                    logger.warning("No jobs to save")
                    return ""

                self.current_df.to_csv(filepath, index=False, encoding='utf-8')

            logger.info(f"✓ Saved CSV: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"CSV save error: {e}")
            return ""

    def save_json(self, filename: Optional[str] = None) -> str:
        """Save scraped jobs to JSON"""
        try:
            DATA_DIR.mkdir(exist_ok=True)

            if filename is None:
                filename = f"linkedin_jobs_{self.timestamp}.json"

            filepath = DATA_DIR / filename

            with self.lock:
                if self.current_df.empty:
                    logger.warning("No jobs to save")
                    return ""

                data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_jobs": len(self.current_df),
                    "jobs": self.current_df.to_dict('records')
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Saved JSON: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"JSON save error: {e}")
            return ""

    def save_both(self, base_filename: Optional[str] = None) -> Dict[str, str]:
        """Save to both CSV and JSON"""
        if base_filename is None:
            base_filename = f"linkedin_jobs_{self.timestamp}"

        return {
            "csv": self.save_csv(f"{base_filename}.csv"),
            "json": self.save_json(f"{base_filename}.json")
        }

# Global scraper manager
scraper_manager = LinkedInScraperManager()

def create_session() -> requests.Session:
    """Create requests session with retry strategy"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_random_user_agent() -> str:
    """Get random user agent"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Linux; Android 13; SM-X906B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

def process_job(job_element, work_type: str, exp_level: str, position: str) -> Optional[Dict]:
    """Process individual job element from LinkedIn"""
    try:
        # Extract job elements
        title_element = job_element.find('h3', class_='base-search-card__title')
        company_element = job_element.find('a', class_='hidden-nested-link')
        loc_element = job_element.find('span', class_='job-search-card__location')
        link_element = job_element.find('a', class_='base-card__full-link')

        # Validate all required fields
        if not all([title_element, company_element, loc_element, link_element]):
            return None

        title = title_element.text.strip()
        company = company_element.text.strip()
        location = loc_element.text.strip()
        link = link_element.get('href', '').split('?')[0]

        if not link:
            return None

        # Fetch job description
        description = "Description not available"
        skills = []

        try:
            time.sleep(random.uniform(2, 5))

            session = create_session()
            response = session.get(
                link,
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Accept-Language': 'en-US,en;q=0.9'
                },
                timeout=10
            )
            response.raise_for_status()

            job_soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple selectors for description
            description_selectors = [
                'div.description__text',
                'div.show-more-less-html__markup',
                'div.core-section-container__content',
                'section.core-section-container'
            ]

            for selector in description_selectors:
                desc_element = job_soup.select_one(selector)
                if desc_element:
                    description = desc_element.get_text('\n').strip()[:1000]
                    skills = get_skills(description)
                    break

        except requests.Timeout:
            logger.warning(f"Timeout fetching {link}")
        except Exception as e:
            logger.debug(f"Error processing job description: {e}")

        return {
            "Position": position,
            "Date": datetime.now().strftime('%Y-%m-%d'),
            "Work_type": work_type,
            "Level": exp_level,
            "Title": title,
            "Company": company,
            "Location": location,
            "Link": link,
            "Description": description,
            "Skills": ", ".join(skills[:5]) if skills else "Not detected"
        }

    except Exception as e:
        logger.error(f"Error processing job card: {e}")
        return None

def scrape_linkedin_jobs(
    position: str,
    location: str,
    work_types: List[str] = None,
    exp_levels: List[str] = None,
    time_filter: str = "Past month",
    max_pages: int = 4
) -> List[Dict]:
    """
    Scrape jobs from LinkedIn

    Args:
        position: Job position to search
        location: Job location
        work_types: List of work types (On-site, Hybrid, Remote)
        exp_levels: List of experience levels (Internship, Entry level, Associate, Mid-Senior level)
        time_filter: Time filter (Past 24 hours, Past week, Past month)
        max_pages: Maximum pages to scrape (each page = 25 jobs)
    """
    if work_types is None:
        work_types = ["Remote", "Hybrid", "On-site"]
    if exp_levels is None:
        exp_levels = ["Entry level", "Associate", "Mid-Senior level"]

    jobs_found = 0
    session = create_session()

    logger.info(f"\n{'='*70}")
    logger.info(f"LinkedIn Job Scraper")
    logger.info(f"Position: {position} | Location: {location}")
    logger.info(f"Work types: {work_types} | Experience levels: {exp_levels}")
    logger.info(f"{'='*70}\n")

    for work_type in work_types:
        if scraper_manager.stop_event.is_set():
            break

        for exp_level in exp_levels:
            if scraper_manager.stop_event.is_set():
                break

            try:
                # Build LinkedIn search URL
                base_url = (
                    f"https://www.linkedin.com/jobs/search/"
                    f"?keywords={position}"
                    f"&location={location}"
                    f"&{work_type_mapping.get(work_type, '')}"
                    f"&{experience_level_mapping.get(exp_level, '')}"
                    f"&{time_filter_mapping.get(time_filter, '')}"
                    f"&radius=0"
                )

                logger.info(f"🔍 Scraping: {work_type} | {exp_level}...")

                # Get first page to estimate total jobs
                try:
                    response = session.get(base_url, timeout=10, headers={'User-Agent': get_random_user_agent()})
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Try to find total jobs count
                    count_element = soup.find('span', class_='results-context-header__job-count')
                    if count_element:
                        try:
                            total_jobs = int(count_element.text.replace(',', ''))
                            logger.info(f"  Found {total_jobs} total jobs")
                        except:
                            total_jobs = 25
                    else:
                        total_jobs = 25
                except Exception as e:
                    logger.warning(f"Could not fetch first page: {e}")
                    total_jobs = 25

                total_jobs = min(total_jobs, 100)  # Limit to 100 per combination

                # Scrape pages
                for start in range(0, total_jobs, 25):
                    if scraper_manager.stop_event.is_set():
                        break

                    if start // 25 >= max_pages:
                        break

                    time.sleep(random.uniform(2, 5))

                    url = f"{base_url}&start={start}"

                    try:
                        response = session.get(url, timeout=10, headers={'User-Agent': get_random_user_agent()})
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')

                        jobs = soup.find_all('div', class_='base-card')
                        logger.info(f"  Page {start // 25 + 1}: Found {len(jobs)} jobs")

                        if not jobs:
                            break

                        # Process jobs
                        for job in jobs:
                            if scraper_manager.stop_event.is_set():
                                break

                            job_data = process_job(job, work_type, exp_level, position)
                            if job_data:
                                scraper_manager.add_job(job_data)
                                jobs_found += 1

                    except requests.Timeout:
                        logger.warning(f"Timeout on page {start // 25 + 1}")
                        break
                    except Exception as e:
                        logger.error(f"Error scraping page {start // 25 + 1}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error in scrape loop: {e}")
                continue

    logger.info(f"\n{'='*70}")
    logger.info(f"✓ Scraping complete: {jobs_found} jobs found")
    logger.info(f"{'='*70}\n")

    return scraper_manager.current_df.to_dict('records')

def scrape_linkedin_and_save(
    position: str,
    location: str,
    work_types: List[str] = None,
    exp_levels: List[str] = None,
    time_filter: str = "Past month",
    max_pages: int = 4
) -> Dict[str, str]:
    """Scrape LinkedIn jobs and save to files"""
    scraper_manager.reset()

    # Scrape jobs
    scrape_linkedin_jobs(
        position=position,
        location=location,
        work_types=work_types,
        exp_levels=exp_levels,
        time_filter=time_filter,
        max_pages=max_pages
    )

    # Save to both formats
    files = scraper_manager.save_both()

    logger.info(f"\n✓ Data saved!")
    logger.info(f"  CSV: {files['csv']}")
    logger.info(f"  JSON: {files['json']}")

    return files

if __name__ == "__main__":
    # Example usage
    files = scrape_linkedin_and_save(
        position="Python Developer",
        location="United States",
        work_types=["Remote", "Hybrid"],
        exp_levels=["Entry level", "Associate"],
        time_filter="Past month",
        max_pages=2
    )

