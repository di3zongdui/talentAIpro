"""
API v1 - 路由模块
"""
from fastapi import APIRouter
from .candidate import router as candidate_router
from .job import router as job_router
from .match import router as match_router

router = APIRouter(prefix="/api/v1")

router.include_router(candidate_router, prefix="/candidates", tags=["candidates"])
router.include_router(job_router, prefix="/jobs", tags=["jobs"])
router.include_router(match_router, prefix="/matches", tags=["matches"])