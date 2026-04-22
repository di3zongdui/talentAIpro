"""
API v1 - 匹配API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...models.match import MatchResult, MatchListResponse, MatchResponse
from ...engine.matching_v1 import MatchingEngineV1
from ..candidate import _candidates_db
from ..job import _jobs_db

router = APIRouter()

# 初始化匹配引擎
_matching_engine = MatchingEngineV1(threshold=75.0)

# 模拟匹配结果存储
_match_results_db: List[MatchResult] = []


class MatchRequest(BaseModel):
    job_id: str
    candidate_ids: Optional[List[str]] = None  # 如果为空，匹配所有候选人


class BatchMatchRequest(BaseModel):
    candidates: List[str]  # 候选人ID列表
    job_id: str


@router.post("/single", response_model=MatchResponse)
async def match_single(job_id: str, candidate_id: str):
    """单对单匹配"""
    # 查找职位
    job = None
    for j in _jobs_db:
        if j.id == job_id:
            job = j
            break

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 查找候选人
    candidate = None
    for c in _candidates_db:
        if c.id == candidate_id:
            candidate = c
            break

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # 执行匹配
    result = _matching_engine.match(job, candidate)

    return MatchResponse(success=True, data=result)


@router.post("/batch", response_model=MatchListResponse)
async def match_batch(request: BatchMatchRequest):
    """批量匹配：一个职位 vs 多个候选人"""
    # 查找职位
    job = None
    for j in _jobs_db:
        if j.id == request.job_id:
            job = j
            break

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 查找候选人
    candidates = []
    for cid in request.candidates:
        for c in _candidates_db:
            if c.id == cid:
                candidates.append(c)
                break

    if not candidates:
        raise HTTPException(status_code=400, detail="No valid candidates found")

    # 执行批量匹配
    results = _matching_engine.batch_match(job, candidates)

    return MatchListResponse(
        success=True,
        data=results,
        total=len(results),
        top_matches=results[:10],  # 返回前10最优匹配
    )


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str):
    """获取匹配结果"""
    for m in _match_results_db:
        if m.id == match_id:
            return MatchResponse(success=True, data=m)

    raise HTTPException(status_code=404, detail="Match not found")


@router.get("/job/{job_id}", response_model=MatchListResponse)
async def get_matches_for_job(
    job_id: str,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
):
    """获取职位的所有匹配结果"""
    results = [m for m in _match_results_db if m.job_id == job_id]

    if min_score:
        results = [m for m in results if m.composite_score >= min_score]

    results.sort(key=lambda x: x.composite_score, reverse=True)

    return MatchListResponse(
        success=True,
        data=results[:limit],
        total=len(results),
        top_matches=results[:10],
    )


@router.get("/candidate/{candidate_id}", response_model=MatchListResponse)
async def get_matches_for_candidate(
    candidate_id: str,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
):
    """获取候选人的所有匹配结果"""
    results = [m for m in _match_results_db if m.candidate_id == candidate_id]

    if min_score:
        results = [m for m in results if m.composite_score >= min_score]

    results.sort(key=lambda x: x.composite_score, reverse=True)

    return MatchListResponse(
        success=True,
        data=results[:limit],
        total=len(results),
        top_matches=results[:10],
    )


@router.get("/top", response_model=MatchListResponse)
async def get_top_matches(
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(60, ge=0, le=100),
):
    """获取全局最优匹配"""
    filtered = [m for m in _match_results_db if m.composite_score >= min_score]
    filtered.sort(key=lambda x: x.composite_score, reverse=True)

    return MatchListResponse(
        success=True,
        data=filtered[:limit],
        total=len(filtered),
        top_matches=filtered[:10],
    )