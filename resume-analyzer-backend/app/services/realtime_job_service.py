import requests
from app.core.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RealTimeJobService:
    @staticmethod
    def search_jobs(query: str, location: str = "Remote") -> List[Dict[str, Any]]:
        """
        Fetches real-time job listings from Google Jobs via SerpApi.
        """
        if not settings.SERPAPI_API_KEY:
            logger.warning("SERPAPI_API_KEY is not set. Real-time search disabled.")
            return []

        try:
            params = {
                "engine": "google_jobs",
                "q": f"{query} in {location}",
                "api_key": settings.SERPAPI_API_KEY,
                "hl": "en", # Language: English
                "gl": "us", # Location: US (default, can be adjusted or passed)
            }
            
            logger.info(f"Fetching jobs from SerpApi for query: {params['q']}")
            response = requests.get("https://serpapi.com/search.json", params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            if "jobs_results" in data:
                for result in data["jobs_results"]:
                    # Extract salary if available
                    salary = "Competitive"
                    if result.get("detected_extensions", {}).get("salary"):
                        salary = result["detected_extensions"]["salary"]
                    
                    # Extract posted date
                    posted = "Recently"
                    if result.get("detected_extensions", {}).get("posted_at"):
                        posted = result["detected_extensions"]["posted_at"]

                    job = {
                        "job_id": result.get("job_id", ""),  # SerpAPI's ID
                        "title": result.get("title", "Unknown Role"),
                        "company": result.get("company_name", "Unknown Company"),
                        "location": result.get("location", location),
                        "salary_range": salary,
                        "posted_date": posted,
                        "description_text": result.get("description", ""),
                        "apply_link": result.get("apply_options", [{}])[0].get("link") if result.get("apply_options") else "#",
                        "logo": result.get("thumbnail", None)
                    }
                    jobs.append(job)
            
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"Error fetching real-time jobs: {e}")
            return []
