"""
TalentAI Pro - 数据模型模块
"""
from .candidate import Candidate, CandidateCreate, CandidateResponse
from .job import Job, JobCreate, JobResponse
from .match import MatchResult, MatchScore

__all__ = [
    "Candidate",
    "CandidateCreate",
    "CandidateResponse",
    "Job",
    "JobCreate",
    "JobResponse",
    "MatchResult",
    "MatchScore",
]
