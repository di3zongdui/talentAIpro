"""
API v1 - 候选人API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...models.candidate import (
    Candidate,
    CandidateCreate,
    CandidateResponse,
    CandidateListResponse,
)

router = APIRouter()

# 模拟数据库
_candidates_db: List[Candidate] = []


@router.post("/", response_model=CandidateResponse)
async def create_candidate(candidate: CandidateCreate):
    """创建候选人"""
    # 生成ID
    candidate_id = f"CAND-{len(_candidates_db) + 1:04d}"

    # 构建完整对象
    candidate_obj = Candidate(
        id=candidate_id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        current_title=candidate.current_title,
        current_company=candidate.current_company,
        expected_salary_min=candidate.expected_salary_min,
        expected_salary_max=candidate.expected_salary_max,
        preferred_locations=candidate.preferred_locations,
        preferred_job_titles=candidate.preferred_job_titles,
        resume_text=candidate.resume_text,
        linkedin_url=candidate.linkedin_url,
        github_url=candidate.github_url,
    )

    _candidates_db.append(candidate_obj)

    return CandidateResponse(success=True, data=candidate_obj)


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str):
    """获取候选人"""
    for c in _candidates_db:
        if c.id == candidate_id:
            return CandidateResponse(success=True, data=c)

    raise HTTPException(status_code=404, detail="Candidate not found")


@router.get("/", response_model=CandidateListResponse)
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = None,
    status: Optional[str] = None,
):
    """列出候选人"""
    filtered = _candidates_db

    if location:
        filtered = [c for c in filtered if c.location and location in c.location]

    if status:
        filtered = [c for c in filtered if c.status == status]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]

    return CandidateListResponse(
        success=True,
        data=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{candidate_id}", response_model=CandidateResponse)
async def delete_candidate(candidate_id: str):
    """删除候选人"""
    global _candidates_db
    for i, c in enumerate(_candidates_db):
        if c.id == candidate_id:
            deleted = _candidates_db.pop(i)
            return CandidateResponse(success=True, data=deleted, message="Deleted")

    raise HTTPException(status_code=404, detail="Candidate not found")


@router.get("/search/by-skill", response_model=CandidateListResponse)
async def search_by_skill(
    skill: str = Query(..., description="技能关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """按技能搜索候选人"""
    filtered = [
        c for c in _candidates_db
        if c.current_title and skill.lower() in c.current_title.lower()
        or (c.github_data and skill.lower() in str(c.github_data).lower())
    ]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size

    return CandidateListResponse(
        success=True,
        data=filtered[start:end],
        total=total,
        page=page,
        page_size=page_size,
    )