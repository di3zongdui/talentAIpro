"""
Candidate Matcher
Matches candidates to job requisitions using semantic search
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import math


@dataclass
class CandidateProfile:
    """Parsed candidate profile"""
    id: str
    name: str
    skills: List[str]
    experience_years: int
    education: str
    location: str
    salary_expectation: Optional[int] = None
    raw_text: str = ""


@dataclass
class JobRequisition:
    """Parsed job requisition"""
    id: str
    title: str
    skills: List[str]
    experience_years_min: int
    experience_years_max: int
    education_min: str
    location: str
    salary_range_min: int
    salary_range_max: int
    raw_text: str = ""


class CandidateMatcher:
    """
    Semantic matching between candidates and jobs

    Uses keyword overlap, skill embedding similarity,
    and constraint satisfaction scoring
    """

    # Skill synonyms mapping
    SKILL_SYNONYMS = {
        "python": ["python", "django", "flask", "fastapi"],
        "javascript": ["javascript", "js", "nodejs", "node"],
        "react": ["react", "reactjs", "react.js"],
        "postgresql": ["postgresql", "postgres", "pg"],
        "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "docker": ["docker", "container", "containerization"],
        "kubernetes": ["kubernetes", "k8s"],
        "ml": ["machine learning", "ml", "ai", "deep learning"],
    }

    def __init__(self):
        self._match_cache: Dict[str, Dict[str, float]] = {}

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name using synonyms"""
        skill_lower = skill.lower()
        for canonical, synonyms in self.SKILL_SYNONYMS.items():
            if skill_lower in synonyms or canonical in skill_lower:
                return canonical
        return skill_lower

    def calculate_skill_similarity(self, candidate_skills: List[str],
                                   job_skills: List[str]) -> float:
        """
        Calculate skill match score using normalized overlap

        Returns 0.0 to 1.0
        """
        if not job_skills:
            return 1.0

        candidate_normalized = {self.normalize_skill(s) for s in candidate_skills}
        job_normalized = {self.normalize_skill(s) for s in job_skills}

        # Jaccard similarity
        intersection = candidate_normalized & job_normalized
        union = candidate_normalized | job_normalized

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def calculate_experience_match(self, candidate_exp: int,
                                   job_exp_min: int,
                                   job_exp_max: int) -> float:
        """
        Calculate experience match score

        Perfect match = 1.0, acceptable range = 0.5+
        """
        if job_exp_min <= candidate_exp <= job_exp_max:
            # Perfect fit
            return 1.0
        elif candidate_exp < job_exp_min:
            # Under-qualified
            return max(0.0, 1.0 - (job_exp_min - candidate_exp) * 0.2)
        else:
            # Over-qualified
            overage = candidate_exp - job_exp_max
            return max(0.3, 1.0 - overage * 0.1)

    def calculate_salary_match(self, candidate_salary: Optional[int],
                              job_salary_min: int,
                              job_salary_max: int) -> float:
        """Calculate salary compatibility"""
        if candidate_salary is None:
            return 0.8  # Neutral if not specified

        if job_salary_min <= candidate_salary <= job_salary_max:
            return 1.0
        elif candidate_salary < job_salary_min:
            # Candidate might be undervaluing
            gap = job_salary_min - candidate_salary
            return max(0.5, 1.0 - gap / job_salary_min * 0.5)
        else:
            # Candidate expects more
            gap = candidate_salary - job_salary_max
            return max(0.0, 1.0 - gap / candidate_salary * 0.8)

    def calculate_location_match(self, candidate_location: str,
                                job_locations: List[str]) -> float:
        """Calculate location compatibility"""
        if not job_locations:
            return 1.0

        # Simple substring matching
        cand_lower = candidate_location.lower()
        for loc in job_locations:
            if loc.lower() in cand_lower or cand_lower in loc.lower():
                return 1.0

        # Check for remote flexibility
        if any("remote" in loc.lower() for loc in job_locations):
            return 0.7

        return 0.3

    def match(self, candidate: Dict[str, Any],
              job: Dict[str, Any],
              weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calculate overall match score

        Returns detailed breakdown
        """
        if weights is None:
            weights = {
                "skills": 0.40,
                "experience": 0.25,
                "salary": 0.20,
                "location": 0.15,
            }

        # Parse candidate
        cand_skills = candidate.get("skills", [])
        cand_exp = candidate.get("experience_years", 0)
        cand_salary = candidate.get("salary_expectation")
        cand_location = candidate.get("location", "")

        # Parse job
        job_skills = job.get("required_skills", [])
        job_exp_min = job.get("experience_years_min", 0)
        job_exp_max = job.get("experience_years_max", 999)
        job_salary_min = job.get("salary_range_min", 0)
        job_salary_max = job.get("salary_range_max", 999999)
        job_locations = job.get("locations", [])

        # Calculate component scores
        skill_score = self.calculate_skill_similarity(cand_skills, job_skills)
        exp_score = self.calculate_experience_match(cand_exp, job_exp_min, job_exp_max)
        salary_score = self.calculate_salary_match(cand_salary, job_salary_min, job_salary_max)
        location_score = self.calculate_location_match(cand_location, job_locations)

        # Weighted total
        total_score = (
            skill_score * weights["skills"] +
            exp_score * weights["experience"] +
            salary_score * weights["salary"] +
            location_score * weights["location"]
        )

        # Identify gaps
        candidate_norm = {self.normalize_skill(s) for s in cand_skills}
        job_norm = {self.normalize_skill(s) for s in job_skills}
        matched_skills = candidate_norm & job_norm
        missing_skills = job_norm - candidate_norm

        return {
            "candidate_id": candidate.get("id"),
            "job_id": job.get("id"),
            "overall_score": round(total_score, 3),
            "breakdown": {
                "skills": {
                    "score": round(skill_score, 3),
                    "weight": weights["skills"],
                    "matched": list(matched_skills),
                    "missing": list(missing_skills),
                },
                "experience": {
                    "score": round(exp_score, 3),
                    "weight": weights["experience"],
                    "candidate_years": cand_exp,
                    "job_range": [job_exp_min, job_exp_max],
                },
                "salary": {
                    "score": round(salary_score, 3),
                    "weight": weights["salary"],
                    "candidate_expectation": cand_salary,
                    "job_range": [job_salary_min, job_salary_max],
                },
                "location": {
                    "score": round(location_score, 3),
                    "weight": weights["location"],
                    "candidate_location": cand_location,
                    "job_locations": job_locations,
                },
            },
            "recommendation": self._generate_recommendation(total_score),
        }

    def batch_match(self, candidates: List[Dict[str, Any]],
                   jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match all candidates to all jobs"""
        results = []
        for candidate in candidates:
            for job in jobs:
                match_result = self.match(candidate, job)
                results.append(match_result)

        # Sort by score
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        return results

    def find_best_matches(self, candidate: Dict[str, Any],
                          jobs: List[Dict[str, Any]],
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """Find top N jobs for a candidate"""
        matches = []
        for job in jobs:
            match_result = self.match(candidate, job)
            matches.append(match_result)

        matches.sort(key=lambda x: x["overall_score"], reverse=True)
        return matches[:top_n]

    def _generate_recommendation(self, score: float) -> str:
        """Generate recommendation based on score"""
        if score >= 0.85:
            return "strong_match"
        elif score >= 0.70:
            return "good_match"
        elif score >= 0.50:
            return "potential_match"
        elif score >= 0.30:
            return "weak_match"
        return "no_match"
