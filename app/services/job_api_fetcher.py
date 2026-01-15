"""
Job APIs Integration Module
Fetches job data from multiple public job APIs
"""
import aiohttp
import asyncio
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobAPIFetcher:
    """Fetch jobs from multiple APIs"""

    def __init__(self):
        self.session = None
        self.jobs = []

    async def init_session(self):
        """Initialize async session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close async session"""
        if self.session:
            await self.session.close()

    async def fetch_github_jobs(self, keyword: str = "python") -> List[Dict]:
        """
        Fetch jobs from GitHub Jobs API (archived but still works)
        """
        try:
            url = f"https://jobs.github.com/positions.json?description={keyword}"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    jobs = await response.json()
                    logger.info(f"✓ Fetched {len(jobs)} jobs from GitHub Jobs API")
                    return [self._format_github_job(job) for job in jobs[:5]]
        except Exception as e:
            logger.warning(f"GitHub Jobs API error: {e}")
        return []

    async def fetch_jooble_jobs(self, keyword: str = "python", location: str = "USA") -> List[Dict]:
        """
        Fetch jobs from Jooble API (free tier available)
        """
        try:
            url = "https://api.jooble.org/api/position/list"
            payload = {
                "keywords": keyword,
                "location": location,
                "pageNum": 1
            }
            async with self.session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get('positions', [])
                    logger.info(f"✓ Fetched {len(jobs)} jobs from Jooble API")
                    return [self._format_jooble_job(job) for job in jobs[:5]]
        except Exception as e:
            logger.warning(f"Jooble API error: {e}")
        return []

    async def fetch_adzuna_jobs(self, keyword: str = "python", location: str = "United States") -> List[Dict]:
        """
        Fetch jobs from Adzuna API (requires free API key, using public endpoint)
        """
        try:
            url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                "what": keyword,
                "where": location,
                "app_id": "demo_app",
                "app_key": "demo_key"
            }
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get('results', [])
                    logger.info(f"✓ Fetched {len(jobs)} jobs from Adzuna API")
                    return [self._format_adzuna_job(job) for job in jobs[:5]]
        except Exception as e:
            logger.warning(f"Adzuna API error: {e}")
        return []

    async def fetch_remoteok_jobs(self, keyword: str = "python") -> List[Dict]:
        """
        Fetch remote jobs from RemoteOK API
        """
        try:
            url = "https://remoteok.io/api"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    jobs = await response.json()
                    # Filter by keyword
                    filtered = [j for j in jobs if keyword.lower() in str(j).lower()][:5]
                    logger.info(f"✓ Fetched {len(filtered)} remote jobs from RemoteOK API")
                    return [self._format_remoteok_job(job) for job in filtered]
        except Exception as e:
            logger.warning(f"RemoteOK API error: {e}")
        return []

    async def fetch_workingnomads_jobs(self) -> List[Dict]:
        """
        Fetch remote jobs from Working Nomads API
        """
        try:
            url = "https://www.workingnomads.co/api/feeds/jobs/"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get('results', [])
                    logger.info(f"✓ Fetched {len(jobs)} jobs from Working Nomads API")
                    return [self._format_workingnomads_job(job) for job in jobs[:5]]
        except Exception as e:
            logger.warning(f"Working Nomads API error: {e}")
        return []

    async def fetch_stackoverflow_jobs(self, keyword: str = "python", location: str = "US") -> List[Dict]:
        """
        Fetch jobs from Stack Overflow API
        """
        try:
            url = "https://api.stackexchange.com/2.3/jobs"
            params = {
                "site": "stackoverflow",
                "sort": "activity",
                "tagged": keyword,
                "location": location
            }
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get('items', [])
                    logger.info(f"✓ Fetched {len(jobs)} jobs from Stack Overflow API")
                    return [self._format_stackoverflow_job(job) for job in jobs[:5]]
        except Exception as e:
            logger.warning(f"Stack Overflow API error: {e}")
        return []

    def _format_github_job(self, job: Dict) -> Dict:
        """Format GitHub Jobs response"""
        return {
            "id": job.get('id'),
            "title": job.get('title', 'N/A'),
            "company": job.get('company', 'N/A'),
            "location": job.get('location', 'Remote'),
            "description": job.get('description', '')[:200],
            "url": job.get('url', ''),
            "posted_at": job.get('created_at', ''),
            "source": "GitHub Jobs"
        }

    def _format_jooble_job(self, job: Dict) -> Dict:
        """Format Jooble response"""
        return {
            "id": job.get('id'),
            "title": job.get('title', 'N/A'),
            "company": job.get('company', 'N/A'),
            "location": job.get('location', 'N/A'),
            "description": job.get('snippet', '')[:200],
            "url": job.get('link', ''),
            "posted_at": job.get('updated', ''),
            "source": "Jooble"
        }

    def _format_adzuna_job(self, job: Dict) -> Dict:
        """Format Adzuna response"""
        return {
            "id": job.get('id'),
            "title": job.get('title', 'N/A'),
            "company": job.get('company', {}).get('display_name', 'N/A'),
            "location": job.get('location', {}).get('display_name', 'N/A'),
            "description": job.get('description', '')[:200],
            "url": job.get('redirect_url', ''),
            "posted_at": job.get('created', ''),
            "source": "Adzuna"
        }

    def _format_remoteok_job(self, job: Dict) -> Dict:
        """Format RemoteOK response"""
        return {
            "id": job.get('id'),
            "title": job.get('title', 'N/A'),
            "company": job.get('company', 'N/A'),
            "location": job.get('location', 'Remote'),
            "description": job.get('description', '')[:200],
            "url": job.get('url', ''),
            "posted_at": job.get('date', ''),
            "source": "RemoteOK"
        }

    def _format_workingnomads_job(self, job: Dict) -> Dict:
        """Format Working Nomads response"""
        return {
            "id": job.get('id'),
            "title": job.get('title', 'N/A'),
            "company": job.get('company', 'N/A'),
            "location": job.get('location', 'Remote'),
            "description": job.get('description', '')[:200],
            "url": job.get('url', ''),
            "posted_at": job.get('published_at', ''),
            "source": "Working Nomads"
        }

    def _format_stackoverflow_job(self, job: Dict) -> Dict:
        """Format Stack Overflow response"""
        return {
            "id": job.get('job_id'),
            "title": job.get('title', 'N/A'),
            "company": job.get('company_name', 'N/A'),
            "location": job.get('location', 'N/A'),
            "description": job.get('description', '')[:200],
            "url": job.get('link', ''),
            "posted_at": job.get('posted_date', ''),
            "source": "Stack Overflow"
        }

    async def fetch_all_jobs(self, keyword: str = "python", location: str = "USA") -> List[Dict]:
        """
        Fetch jobs from all available APIs concurrently
        """
        await self.init_session()

        try:
            tasks = [
                self.fetch_github_jobs(keyword),
                self.fetch_jooble_jobs(keyword, location),
                self.fetch_adzuna_jobs(keyword, location),
                self.fetch_remoteok_jobs(keyword),
                self.fetch_workingnomads_jobs(),
                self.fetch_stackoverflow_jobs(keyword, location),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_jobs = []
            for result in results:
                if isinstance(result, list):
                    all_jobs.extend(result)

            logger.info(f"✓ Total jobs fetched from all APIs: {len(all_jobs)}")
            return all_jobs

        finally:
            await self.close_session()


async def get_jobs_from_apis(keyword: str = "python", location: str = "USA") -> List[Dict]:
    """
    Convenience function to fetch all jobs
    """
    fetcher = JobAPIFetcher()
    return await fetcher.fetch_all_jobs(keyword, location)


# Synchronous wrapper for non-async contexts
def get_jobs_sync(keyword: str = "python", location: str = "USA") -> List[Dict]:
    """
    Synchronous wrapper for fetching jobs
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_jobs_from_apis(keyword, location))
    finally:
        loop.close()

