"""
API v1 - 职位API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...models.job import Job, JobCreate, JobResponse, JobListResponse

router = APIRouter()

# 模拟数据库
_jobs_db: List[Job] = []


@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate, created_by: str = "system"):
    """创建职位"""
    job_id = f"JOB-{len(_jobs_db) + 1:04d}"

    job_obj = Job(
        id=job_id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        job_type=job.job_type,
        description=job.description,
        requirements=job.requirements,
        department=job.department,
        headcount=job.headcount,
        urgency=job.urgency,
        created_by=created_by,
    )

    _jobs_db.append(job_obj)

    return JobResponse(success=True, data=job_obj)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """获取职位"""
    for j in _jobs_db:
        if j.id == job_id:
            return JobResponse(success=True, data=j)

    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = None,
    status: Optional[str] = None,
    company: Optional[str] = None,
):
    """列出职位"""
    filtered = _jobs_db

    if location:
        filtered = [j for j in filtered if location in j.location]

    if status:
        filtered = [j for j in filtered if j.status == status]

    if company:
        filtered = [j for j in filtered if company in j.company_name]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]

    return JobListResponse(
        success=True,
        data=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{job_id}", response_model=JobResponse)
async def delete_job(job_id: str):
    """删除职位"""
    global _jobs_db
    for i, j in enumerate(_jobs_db):
        if j.id == job_id:
            deleted = _jobs_db.pop(i)
            return JobResponse(success=True, data=deleted, message="Deleted")

    raise HTTPException(status_code=404, detail="Job not found")


@router.patch("/{job_id}/status")
async def update_job_status(job_id: str, status: str = Query(...)):
    """更新职位状态"""
    for j in _jobs_db:
        if j.id == job_id:
            j.status = status
            return {"success": True, "message": f"Status updated to {status}"}

    raise HTTPException(status_code=404, detail="Job not found")