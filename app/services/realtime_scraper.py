"""
Real-time Job Data Scraper
Fetches live job data from multiple sources and saves to JSON/CSV files
"""

import json
import csv
import requests
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directories
DATA_DIR = Path("scraped_data")
DATA_DIR.mkdir(exist_ok=True)

class RealTimeJobScraper:
    """Scrape real-time job data from multiple APIs"""

    def __init__(self):
        self.jobs = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def fetch_remoteok_jobs(self, keyword: str = "python", limit: int = 50) -> List[Dict]:
        """Fetch real-time jobs from RemoteOK API"""
        try:
            print(f"📌 Fetching RemoteOK jobs for '{keyword}'...")
            url = "https://remoteok.io/api"
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            data = response.json()

            jobs = []
            for entry in (data if isinstance(data, list) else []):
                if not isinstance(entry, dict):
                    continue

                title = entry.get("position") or entry.get("title")
                if not title or keyword.lower() not in str(entry).lower():
                    continue

                job = {
                    "id": entry.get("id") or entry.get("slug"),
                    "title": title,
                    "company": entry.get("company") or "Unknown",
                    "location": entry.get("location") or "Remote",
                    "description": (entry.get("description") or "")[:500],
                    "url": entry.get("url") or entry.get("apply_url") or "",
                    "salary": entry.get("salary") or "Not specified",
                    "posted_at": entry.get("date") or entry.get("published_at") or datetime.now().isoformat(),
                    "source": "RemoteOK",
                    "tags": entry.get("tags") or []
                }
                jobs.append(job)

                if len(jobs) >= limit:
                    break

            print(f"✓ RemoteOK: {len(jobs)} jobs found")
            return jobs
        except Exception as e:
            print(f"✗ RemoteOK error: {e}")
            return []

    def fetch_github_jobs(self, keyword: str = "python", limit: int = 30) -> List[Dict]:
        """Fetch real-time jobs from GitHub Jobs API"""
        try:
            print(f"📌 Fetching GitHub Jobs for '{keyword}'...")
            url = f"https://jobs.github.com/positions.json?description={keyword}"
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            data = response.json()

            jobs = []
            for entry in (data if isinstance(data, list) else []):
                if not isinstance(entry, dict):
                    continue

                job = {
                    "id": entry.get("id"),
                    "title": entry.get("title") or "Unknown",
                    "company": entry.get("company") or "Unknown",
                    "location": entry.get("location") or "Remote",
                    "description": (entry.get("description") or "")[:500],
                    "url": entry.get("url") or "",
                    "salary": "Not specified",
                    "posted_at": entry.get("created_at") or datetime.now().isoformat(),
                    "source": "GitHub Jobs",
                    "tags": entry.get("type") or []
                }
                jobs.append(job)

                if len(jobs) >= limit:
                    break

            print(f"✓ GitHub Jobs: {len(jobs)} jobs found")
            return jobs
        except Exception as e:
            print(f"✗ GitHub Jobs error: {e}")
            return []

    def fetch_adzuna_jobs(self, keyword: str = "python", location: str = "US", limit: int = 30) -> List[Dict]:
        """Fetch real-time jobs from Adzuna API"""
        try:
            print(f"📌 Fetching Adzuna jobs for '{keyword}' in {location}...")
            url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                "what": keyword,
                "where": location,
                "app_id": "demo_app",
                "app_key": "demo_key"
            }
            response = requests.get(url, params=params, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            data = response.json()

            jobs = []
            for entry in (data.get("results", []) if isinstance(data, dict) else []):
                if not isinstance(entry, dict):
                    continue

                job = {
                    "id": entry.get("id"),
                    "title": entry.get("title") or "Unknown",
                    "company": entry.get("company", {}).get("display_name") or "Unknown",
                    "location": entry.get("location", {}).get("display_name") or "Unknown",
                    "description": (entry.get("description") or "")[:500],
                    "url": entry.get("redirect_url") or "",
                    "salary": entry.get("salary_max") or "Not specified",
                    "posted_at": entry.get("created") or datetime.now().isoformat(),
                    "source": "Adzuna",
                    "tags": []
                }
                jobs.append(job)

                if len(jobs) >= limit:
                    break

            print(f"✓ Adzuna: {len(jobs)} jobs found")
            return jobs
        except Exception as e:
            print(f"✗ Adzuna error: {e}")
            return []

    def scrape_all(self, keyword: str = "python", limit_per_source: int = 30) -> List[Dict]:
        """Scrape from all sources"""
        print(f"\n{'='*70}")
        print(f"REAL-TIME JOB SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Keyword: {keyword} | Limit per source: {limit_per_source}")
        print(f"{'='*70}\n")

        # Fetch from all sources
        all_jobs = []
        all_jobs.extend(self.fetch_remoteok_jobs(keyword, limit_per_source))
        time.sleep(2)  # Respect API rate limits

        all_jobs.extend(self.fetch_github_jobs(keyword, limit_per_source))
        time.sleep(2)

        all_jobs.extend(self.fetch_adzuna_jobs(keyword, limit_per_source=limit_per_source))

        # Remove duplicates by title + company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job["title"].lower(), job["company"].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        self.jobs = unique_jobs
        print(f"\n{'='*70}")
        print(f"✓ TOTAL: {len(self.jobs)} unique jobs scraped")
        print(f"{'='*70}\n")

        return self.jobs

    def save_json(self, filename: str = None) -> str:
        """Save jobs to JSON file"""
        if not filename:
            filename = f"jobs_{self.timestamp}.json"

        filepath = DATA_DIR / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_jobs": len(self.jobs),
                    "sources": list(set(j["source"] for j in self.jobs)),
                    "jobs": self.jobs
                }, f, indent=2, ensure_ascii=False)

            print(f"✓ Saved to JSON: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"✗ JSON save error: {e}")
            return ""

    def save_csv(self, filename: str = None) -> str:
        """Save jobs to CSV file"""
        if not filename:
            filename = f"jobs_{self.timestamp}.csv"

        filepath = DATA_DIR / filename
        try:
            if not self.jobs:
                print("✗ No jobs to save")
                return ""

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    "id", "title", "company", "location", "description",
                    "url", "salary", "posted_at", "source", "tags"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for job in self.jobs:
                    row = {key: job.get(key, "") for key in fieldnames}
                    row["tags"] = ",".join(row["tags"]) if isinstance(row["tags"], list) else row["tags"]
                    writer.writerow(row)

            print(f"✓ Saved to CSV: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"✗ CSV save error: {e}")
            return ""

    def save_both(self, base_filename: str = None) -> Dict[str, str]:
        """Save to both JSON and CSV"""
        if not base_filename:
            base_filename = f"jobs_{self.timestamp}"

        return {
            "json": self.save_json(f"{base_filename}.json"),
            "csv": self.save_csv(f"{base_filename}.csv")
        }

    def print_summary(self):
        """Print summary of scraped jobs"""
        if not self.jobs:
            print("No jobs scraped")
            return

        print(f"\n{'='*70}")
        print("JOBS SUMMARY")
        print(f"{'='*70}")
        print(f"Total jobs: {len(self.jobs)}")
        print(f"\nBy source:")
        for source in set(j["source"] for j in self.jobs):
            count = len([j for j in self.jobs if j["source"] == source])
            print(f"  • {source}: {count}")

        print(f"\nFirst 5 jobs:")
        for i, job in enumerate(self.jobs[:5], 1):
            print(f"\n  {i}. {job['title']}")
            print(f"     Company: {job['company']}")
            print(f"     Location: {job['location']}")
            print(f"     Source: {job['source']}")


def scrape_and_save(keyword: str = "python", limit_per_source: int = 30) -> Dict[str, str]:
    """Main function to scrape and save real-time job data"""
    scraper = RealTimeJobScraper()

    # Scrape from all sources
    scraper.scrape_all(keyword=keyword, limit_per_source=limit_per_source)

    # Print summary
    scraper.print_summary()

    # Save to both formats
    files = scraper.save_both()

    print(f"\n✓ Real-time data saved!")
    print(f"  JSON: {files['json']}")
    print(f"  CSV: {files['csv']}")

    return files


if __name__ == "__main__":
    # Example: Scrape Python jobs and save
    scrape_and_save(keyword="python", limit_per_source=30)

    # You can also use it programmatically:
    # scraper = RealTimeJobScraper()
    # jobs = scraper.scrape_all(keyword="javascript", limit_per_source=20)
    # scraper.save_both()

