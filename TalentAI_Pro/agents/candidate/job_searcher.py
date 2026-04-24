"""
Job Searcher
Intelligent job search across multiple platforms
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re


@dataclass
class JobListing:
    """Structured job listing"""
    id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    remote: bool
    skills: List[str]
    description: str
    source: str  # Platform source
    posted_date: str
    url: str


class JobSearcher:
    """
    Intelligent job search with deduplication and ranking

    Features:
    - Multi-platform search
    - Job deduplication
    - Smart ranking based on candidate profile
    - Salary normalization
    """

    # Job title synonyms
    TITLE_SYNONYMS = {
        "senior": ["senior", "sr.", "sr", "lead", "principal", "staff"],
        "junior": ["junior", "jr.", "jr", "entry", "associate"],
        "engineer": ["engineer", "developer", "programmer"],
        "manager": ["manager", "lead", "head", "director"],
    }

    def __init__(self):
        self._search_history: List[Dict[str, Any]] = []
        self._saved_searches: Dict[str, Dict[str, Any]] = {}

    def search(self, query: str, filters: Dict[str, Any] = None) -> List[JobListing]:
        """
        Search for jobs with query and filters

        query: "Senior Python Engineer"
        filters: {
            "location": "北京",
            "remote": True,
            "salary_min": 30000,
            "skills": ["Python", "FastAPI"],
        }
        """
        if filters is None:
            filters = {}

        # Normalize query
        normalized_query = self._normalize_job_title(query)

        # Search across sources (mock for now)
        results = self._search_all_sources(normalized_query, filters)

        # Deduplicate
        unique_jobs = self._deduplicate_jobs(results)

        # Rank by relevance
        ranked_jobs = self._rank_jobs(unique_jobs, filters)

        # Save search
        self._search_history.append({
            "query": query,
            "filters": filters,
            "results_count": len(ranked_jobs),
            "timestamp": str(datetime.now()),
        })

        return ranked_jobs

    def _normalize_job_title(self, title: str) -> str:
        """Normalize job title to standard form"""
        title_lower = title.lower()

        # Expand common abbreviations
        replacements = {
            "sr.": "senior",
            "sr ": "senior ",
            "jr.": "junior",
            "jr ": "junior ",
            "eng": "engineer",
            "dev": "developer",
        }

        for old, new in replacements.items():
            title_lower = title_lower.replace(old, new)

        return title_lower

    def _search_all_sources(self, query: str, filters: Dict[str, Any]) -> List[JobListing]:
        """Search across all job sources"""
        # In production, would call multiple APIs
        # For now, return mock results
        mock_results = self._get_mock_results(query, filters)
        return mock_results

    def _get_mock_results(self, query: str, filters: Dict[str, Any]) -> List[JobListing]:
        """Get mock search results"""
        return [
            JobListing(
                id="job_001",
                title="Senior Python Engineer",
                company="字节跳动",
                location="北京",
                salary_min=35000,
                salary_max=50000,
                remote=True,
                skills=["Python", "FastAPI", "PostgreSQL"],
                description="Lead backend development...",
                source="linkedin",
                posted_date="2026-04-20",
                url="https://example.com/job/001",
            ),
            JobListing(
                id="job_002",
                title="Python Developer",
                company="某知名外企",
                location="上海",
                salary_min=30000,
                salary_max=45000,
                remote=False,
                skills=["Python", "Django", "MySQL"],
                description="Backend development team...",
                source="zhilian",
                posted_date="2026-04-18",
                url="https://example.com/job/002",
            ),
        ]

    def _deduplicate_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """Remove duplicate job listings"""
        seen = set()
        unique = []

        for job in jobs:
            # Create fingerprint
            fingerprint = (
                job.title.lower(),
                job.company.lower(),
                job.location.lower(),
            )

            if fingerprint not in seen:
                seen.add(fingerprint)
                unique.append(job)

        return unique

    def _rank_jobs(self, jobs: List[JobListing],
                   filters: Dict[str, Any]) -> List[JobListing]:
        """Rank jobs by relevance to filters"""

        def job_score(job: JobListing) -> float:
            score = 0.0

            # Skills match
            filter_skills = set(filters.get("skills", []))
            if filter_skills:
                job_skills = set(s.lower() for s in job.skills)
                skill_match = len(filter_skills & job_skills) / len(filter_skills)
                score += skill_match * 0.5

            # Location match
            filter_location = filters.get("location", "").lower()
            if filter_location:
                if filter_location in job.location.lower():
                    score += 0.2
                elif "remote" in job.location.lower() or job.remote:
                    score += 0.15

            # Salary match
            salary_min = filters.get("salary_min", 0)
            if salary_min and job.salary_max:
                if job.salary_max >= salary_min:
                    score += 0.2
                else:
                    score += (job.salary_max / salary_min) * 0.2

            # Recency bonus
            score += 0.1  # Simplified

            return score

        return sorted(jobs, key=job_score, reverse=True)

    def create_alert(self, name: str, query: str,
                     filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a job search alert"""
        alert_id = f"alert_{len(self._saved_searches) + 1}"

        alert = {
            "id": alert_id,
            "name": name,
            "query": query,
            "filters": filters,
            "frequency": "daily",  # daily, weekly
            "active": True,
            "last_run": None,
            "results_count": 0,
        }

        self._saved_searches[alert_id] = alert
        return alert

    def get_alerts(self) -> List[Dict[str, Any]]:
        return list(self._saved_searches.values())


# Need datetime
from datetime import datetime
