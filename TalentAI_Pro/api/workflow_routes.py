"""
Workflow API - 招聘和求职工作流引擎

提供完整的招聘和求职流程支持：
- 招聘流程: 创建职位 → 搜索候选人 → 匹配 → 面试 → 评估 → 谈判 → 录用
- 求职流程: 创建简历 → 搜索职位 → 投递 → 面试 → 谈判 → 接受Offer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/api/workflow", tags=["Workflow"])

# ========== 枚举定义 ==========

class WorkflowType(str, Enum):
    """工作流类型"""
    RECRUITER = "recruiter"  # 招聘流程
    CANDIDATE = "candidate"  # 求职流程

class WorkflowStage(str, Enum):
    """工作流阶段"""
    # 招聘流程
    JOB_CREATED = "job_created"
    CANDIDATES_FOUND = "candidates_found"
    MATCHING_DONE = "matching_done"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    EVALUATION_DONE = "evaluation_done"
    NEGOTIATION_DONE = "negotiation_done"
    HIRED = "hired"
    REJECTED = "rejected"

    # 求职流程
    PROFILE_CREATED = "profile_created"
    JOBS_FOUND = "jobs_found"
    APPLIED = "applied"
    INTERVIEW_PASSED = "interview_passed"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"


class WorkflowDirection(str, Enum):
    """工作流方向"""
    FORWARD = "forward"   # 正向
    BACKWARD = "backward"  # 反向


# ========== 数据模型 ==========

class Job(BaseModel):
    """职位模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    company: str
    requirements: List[str]
    salary_range: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Candidate(BaseModel):
    """候选人模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    email: str
    skills: List[str]
    experience: Optional[str] = None
    expected_salary: Optional[str] = None
    resume: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class MatchResult(BaseModel):
    """匹配结果"""
    job_id: str
    candidate_id: str
    match_score: float = Field(ge=0, le=1)
    matched_skills: List[str] = []
    missing_skills: List[str] = []


# ========== Request Models ==========

class CreateJobRequest(BaseModel):
    """创建职位请求"""
    title: str
    company: str
    requirements: List[str]
    salary_range: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class CreateProfileRequest(BaseModel):
    """创建简历请求"""
    name: str
    email: str
    skills: List[str]
    experience: Optional[str] = None
    expected_salary: Optional[str] = None


class InterviewRecord(BaseModel):
    """面试记录"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    job_id: str
    candidate_id: str
    questions: List[str] = []
    answers: List[str] = []
    evaluation: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)


class NegotiationRecord(BaseModel):
    """谈判记录"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    job_id: str
    candidate_id: str
    initial_offer: Optional[str] = None
    counter_offer: Optional[str] = None
    final_deal: Optional[str] = None
    status: str = "pending"  # pending, negotiating, agreed, rejected
    messages: List[Dict[str, str]] = []


class WorkflowInstance(BaseModel):
    """工作流实例"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: WorkflowType
    current_stage: str
    direction: WorkflowDirection = WorkflowDirection.FORWARD
    job: Optional[Job] = None
    candidate: Optional[Candidate] = None
    matches: List[MatchResult] = []
    interviews: List[InterviewRecord] = []
    negotiations: List[NegotiationRecord] = []
    history: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ========== 存储 ==========

_workflows: Dict[str, WorkflowInstance] = {}
_jobs: Dict[str, Job] = {}
_candidates: Dict[str, Candidate] = {}


# ========== 招聘工作流 API ==========

@router.post("/recruiter/create-job")
async def create_job(request: CreateJobRequest) -> Dict[str, Any]:
    """创建职位 - 招聘流程第1步"""
    job = Job(
        title=request.title,
        company=request.company,
        requirements=request.requirements,
        salary_range=request.salary_range,
        location=request.location,
        description=request.description
    )
    _jobs[job.id] = job

    # 创建工作流实例
    workflow = WorkflowInstance(
        type=WorkflowType.RECRUITER,
        current_stage=WorkflowStage.JOB_CREATED,
        job=job
    )
    workflow.history.append({
        "stage": WorkflowStage.JOB_CREATED,
        "action": "create_job",
        "timestamp": datetime.now().isoformat(),
        "data": {"job_id": job.id, "title": request.title}
    })
    _workflows[workflow.id] = workflow

    return {
        "success": True,
        "workflow_id": workflow.id,
        "job_id": job.id,
        "stage": WorkflowStage.JOB_CREATED,
        "message": f"职位 '{title}' 已创建，等待搜索候选人",
        "next_action": "search_candidates"
    }


@router.post("/recruiter/search-candidates")
async def search_candidates(workflow_id: str, skills: List[str]) -> Dict[str, Any]:
    """搜索候选人 - 招聘流程第2步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    if workflow.type != WorkflowType.RECRUITER:
        raise HTTPException(status_code=400, detail="不是招聘工作流")

    # 模拟搜索候选人
    found_candidates = [
        Candidate(
            id=str(uuid.uuid4())[:8],
            name=f"候选人_{i+1}",
            email=f"candidate{i+1}@example.com",
            skills=skills[:min(len(skills), 3)],
            experience="5年相关经验"
        )
        for i in range(3)
    ]

    for c in found_candidates:
        _candidates[c.id] = c

    workflow.current_stage = WorkflowStage.CANDIDATES_FOUND
    workflow.history.append({
        "stage": WorkflowStage.CANDIDATES_FOUND,
        "action": "search_candidates",
        "timestamp": datetime.now().isoformat(),
        "data": {"candidates_found": len(found_candidates)}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.CANDIDATES_FOUND,
        "candidates": [c.model_dump() for c in found_candidates],
        "message": f"找到 {len(found_candidates)} 位候选人",
        "next_action": "match_candidates"
    }


@router.post("/recruiter/match")
async def match_candidates(workflow_id: str, candidate_ids: List[str]) -> Dict[str, Any]:
    """匹配候选人和职位 - 招聘流程第3步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    job = workflow.job

    matches = []
    for cid in candidate_ids:
        if cid not in _candidates:
            continue
        candidate = _candidates[cid]

        # 计算匹配度
        matched = set(job.requirements) & set(candidate.skills)
        missing = set(job.requirements) - set(candidate.skills)
        score = len(matched) / len(job.requirements) if job.requirements else 0

        match = MatchResult(
            job_id=job.id,
            candidate_id=cid,
            match_score=score,
            matched_skills=list(matched),
            missing_skills=list(missing)
        )
        matches.append(match)
        workflow.matches.append(match)

    workflow.current_stage = WorkflowStage.MATCHING_DONE
    workflow.history.append({
        "stage": WorkflowStage.MATCHING_DONE,
        "action": "match_candidates",
        "timestamp": datetime.now().isoformat(),
        "data": {"matches": len(matches)}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.MATCHING_DONE,
        "matches": [m.model_dump() for m in matches],
        "message": f"匹配完成，{len(matches)} 位候选人符合条件",
        "next_action": "schedule_interview"
    }


@router.post("/recruiter/schedule-interview")
async def schedule_interview(workflow_id: str, candidate_id: str,
                             questions: List[str] = None) -> Dict[str, Any]:
    """安排面试 - 招聘流程第4步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    job = workflow.job

    # 生成默认问题
    if not questions:
        questions = [
            f"请介绍一下您对 {job.title} 职位的理解",
            "您最擅长的技术是什么？",
            "您期望的薪资范围是多少？",
            "为什么想加入我们公司？"
        ]

    interview = InterviewRecord(
        job_id=job.id,
        candidate_id=candidate_id,
        questions=questions
    )
    workflow.interviews.append(interview)

    workflow.current_stage = WorkflowStage.INTERVIEW_SCHEDULED
    workflow.direction = WorkflowDirection.FORWARD
    workflow.history.append({
        "stage": WorkflowStage.INTERVIEW_SCHEDULED,
        "action": "schedule_interview",
        "direction": "forward",
        "timestamp": datetime.now().isoformat(),
        "data": {"candidate_id": candidate_id, "questions_count": len(questions)}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "interview_id": interview.id,
        "stage": WorkflowStage.INTERVIEW_SCHEDULED,
        "questions": questions,
        "message": f"面试已安排，等待候选人回答",
        "next_action": "submit_interview_answer"
    }


@router.post("/recruiter/evaluate")
async def evaluate_interview(workflow_id: str, interview_id: str,
                            answers: List[str], score: float = None) -> Dict[str, Any]:
    """评估面试 - 招聘流程第5步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]

    # 找到面试记录
    interview = None
    for i in workflow.interviews:
        if i.id == interview_id:
            interview = i
            break

    if not interview:
        raise HTTPException(status_code=404, detail="面试记录不存在")

    interview.answers = answers

    # LLM评估（这里简化处理）
    if score is None:
        score = 0.85  # 模拟高分

    evaluation = {
        "technical": score,
        "communication": score - 0.05,
        "culture_fit": score + 0.05,
        "overall": score
    }

    interview.evaluation = evaluation
    interview.score = score

    workflow.current_stage = WorkflowStage.EVALUATION_DONE
    workflow.history.append({
        "stage": WorkflowStage.EVALUATION_DONE,
        "action": "evaluate",
        "timestamp": datetime.now().isoformat(),
        "data": {"score": score, "evaluation": evaluation}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.EVALUATION_DONE,
        "evaluation": evaluation,
        "score": score,
        "message": f"评估完成，综合得分 {score:.0%}",
        "next_action": "start_negotiation" if score >= 0.7 else "reject_candidate"
    }


@router.post("/recruiter/negotiate")
async def start_negotiation(workflow_id: str, candidate_id: str,
                            initial_offer: str = None) -> Dict[str, Any]:
    """开始谈判 - 招聘流程第6步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    job = workflow.job

    negotiation = NegotiationRecord(
        job_id=job.id,
        candidate_id=candidate_id,
        initial_offer=initial_offer or job.salary_range or "面议",
        status="negotiating"
    )
    workflow.negotiations.append(negotiation)

    workflow.current_stage = WorkflowStage.NEGOTIATION_DONE
    workflow.history.append({
        "stage": WorkflowStage.NEGOTIATION_DONE,
        "action": "negotiate",
        "timestamp": datetime.now().isoformat(),
        "data": {"candidate_id": candidate_id, "initial_offer": initial_offer}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "negotiation_id": negotiation.id,
        "stage": WorkflowStage.NEGOTIATION_DONE,
        "initial_offer": negotiation.initial_offer,
        "message": "谈判已开始，等待候选人回复",
        "next_action": "finalize_hire"
    }


@router.post("/recruiter/hire")
async def hire_candidate(workflow_id: str, candidate_id: str,
                         final_deal: str = None) -> Dict[str, Any]:
    """录用候选人 - 招聘流程第7步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    workflow.current_stage = WorkflowStage.HIRED
    workflow.history.append({
        "stage": WorkflowStage.HIRED,
        "action": "hire",
        "direction": "forward",
        "timestamp": datetime.now().isoformat(),
        "data": {"candidate_id": candidate_id, "final_deal": final_deal}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.HIRED,
        "message": "🎉 招聘流程完成！候选人已录用",
        "candidate_id": candidate_id
    }


@router.post("/recruiter/reject")
async def reject_candidate(workflow_id: str, candidate_id: str,
                           reason: str = None) -> Dict[str, Any]:
    """拒绝候选人 - 反向操作"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    workflow.current_stage = WorkflowStage.REJECTED
    workflow.direction = WorkflowDirection.BACKWARD
    workflow.history.append({
        "stage": WorkflowStage.REJECTED,
        "action": "reject",
        "direction": "backward",
        "timestamp": datetime.now().isoformat(),
        "data": {"candidate_id": candidate_id, "reason": reason}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.REJECTED,
        "message": f"候选人已拒绝: {reason or '综合评估不通过'}",
        "next_action": "search_candidates"  # 可以重新搜索
    }


# ========== 求职工作流 API ==========

@router.post("/candidate/create-profile")
async def create_profile(request: CreateProfileRequest) -> Dict[str, Any]:
    """创建简历 - 求职流程第1步"""
    candidate = Candidate(
        name=request.name,
        email=request.email,
        skills=request.skills,
        experience=request.experience,
        expected_salary=request.expected_salary
    )
    _candidates[candidate.id] = candidate

    # 创建工作流实例
    workflow = WorkflowInstance(
        type=WorkflowType.CANDIDATE,
        current_stage=WorkflowStage.PROFILE_CREATED,
        candidate=candidate
    )
    workflow.history.append({
        "stage": WorkflowStage.PROFILE_CREATED,
        "action": "create_profile",
        "timestamp": datetime.now().isoformat(),
        "data": {"candidate_id": candidate.id, "name": request.name}
    })
    _workflows[workflow.id] = workflow

    return {
        "success": True,
        "workflow_id": workflow.id,
        "candidate_id": candidate.id,
        "stage": WorkflowStage.PROFILE_CREATED,
        "message": f"简历已创建，等待搜索职位",
        "next_action": "search_jobs"
    }


@router.post("/candidate/search-jobs")
async def search_jobs(workflow_id: str, keywords: List[str],
                      location: str = None) -> Dict[str, Any]:
    """搜索职位 - 求职流程第2步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    if workflow.type != WorkflowType.CANDIDATE:
        raise HTTPException(status_code=400, detail="不是求职工作流")

    # 模拟搜索职位
    found_jobs = [
        Job(
            id=str(uuid.uuid4())[:8],
            title=f"{keywords[0] if keywords else '工程师'}_{i+1}",
            company=f"公司_{i+1}",
            requirements=keywords[:min(len(keywords), 3)] if keywords else ["Python", "AI"],
            salary_range="30-50K",
            location=location or "深圳"
        )
        for i in range(3)
    ]

    for j in found_jobs:
        _jobs[j.id] = j

    workflow.current_stage = WorkflowStage.JOBS_FOUND
    workflow.history.append({
        "stage": WorkflowStage.JOBS_FOUND,
        "action": "search_jobs",
        "timestamp": datetime.now().isoformat(),
        "data": {"jobs_found": len(found_jobs)}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.JOBS_FOUND,
        "jobs": [j.model_dump() for j in found_jobs],
        "message": f"找到 {len(found_jobs)} 个匹配职位",
        "next_action": "apply_job"
    }


@router.post("/candidate/apply")
async def apply_job(workflow_id: str, job_id: str) -> Dict[str, Any]:
    """投递简历 - 求职流程第3步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]

    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="职位不存在")

    workflow.current_stage = WorkflowStage.APPLIED
    workflow.job = _jobs[job_id]
    workflow.history.append({
        "stage": WorkflowStage.APPLIED,
        "action": "apply",
        "timestamp": datetime.now().isoformat(),
        "data": {"job_id": job_id}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.APPLIED,
        "job": workflow.job.model_dump(),
        "message": "简历已投递，等待面试通知",
        "next_action": "wait_for_interview"
    }


@router.post("/candidate/record-interview")
async def record_interview_result(workflow_id: str, passed: bool,
                                  score: float = None) -> Dict[str, Any]:
    """记录面试结果 - 求职流程第4步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]

    if passed:
        workflow.current_stage = WorkflowStage.INTERVIEW_PASSED
        message = "🎉 面试通过！等待收到Offer"
        next_action = "receive_offer"
    else:
        workflow.current_stage = WorkflowStage.REJECTED
        message = "面试未通过，可以继续申请其他职位"
        next_action = "search_jobs"

    workflow.history.append({
        "stage": workflow.current_stage,
        "action": "interview_result",
        "timestamp": datetime.now().isoformat(),
        "data": {"passed": passed, "score": score}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": workflow.current_stage,
        "message": message,
        "next_action": next_action
    }


@router.post("/candidate/receive-offer")
async def receive_offer(workflow_id: str, offer_details: str = None) -> Dict[str, Any]:
    """收到Offer - 求职流程第5步"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    workflow.current_stage = WorkflowStage.OFFER_RECEIVED

    workflow.history.append({
        "stage": WorkflowStage.OFFER_RECEIVED,
        "action": "receive_offer",
        "timestamp": datetime.now().isoformat(),
        "data": {"offer_details": offer_details}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.OFFER_RECEIVED,
        "offer_details": offer_details or "年薪 40-60万 + 期权",
        "message": "收到Offer！请决定是否接受",
        "next_action": "accept_offer or decline_offer"
    }


@router.post("/candidate/accept-offer")
async def accept_offer(workflow_id: str) -> Dict[str, Any]:
    """接受Offer - 求职流程第6步（完成）"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    workflow.current_stage = WorkflowStage.OFFER_ACCEPTED
    workflow.direction = WorkflowDirection.FORWARD
    workflow.history.append({
        "stage": WorkflowStage.OFFER_ACCEPTED,
        "action": "accept_offer",
        "direction": "forward",
        "timestamp": datetime.now().isoformat(),
        "data": {}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.OFFER_ACCEPTED,
        "message": "🎉 恭喜！Offer已接受，求职流程完成！",
        "company": workflow.job.company if workflow.job else "",
        "title": workflow.job.title if workflow.job else ""
    }


@router.post("/candidate/decline-offer")
async def decline_offer(workflow_id: str, reason: str = None) -> Dict[str, Any]:
    """拒绝Offer - 反向操作"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]
    workflow.current_stage = WorkflowStage.OFFER_DECLINED
    workflow.direction = WorkflowDirection.BACKWARD
    workflow.history.append({
        "stage": WorkflowStage.OFFER_DECLINED,
        "action": "decline_offer",
        "direction": "backward",
        "timestamp": datetime.now().isoformat(),
        "data": {"reason": reason}
    })
    workflow.updated_at = datetime.now()

    return {
        "success": True,
        "workflow_id": workflow_id,
        "stage": WorkflowStage.OFFER_DECLINED,
        "message": f"已拒绝Offer: {reason or '综合考虑'}",
        "next_action": "search_jobs"
    }


# ========== 工作流状态查询 ==========

@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """获取工作流状态"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = _workflows[workflow_id]

    return {
        "id": workflow.id,
        "type": workflow.type,
        "current_stage": workflow.current_stage,
        "direction": workflow.direction,
        "stage_display": get_stage_display(workflow.type, workflow.current_stage),
        "history": workflow.history,
        "created_at": workflow.created_at.isoformat(),
        "updated_at": workflow.updated_at.isoformat()
    }


def get_stage_display(workflow_type: WorkflowType, stage: str) -> str:
    """获取阶段显示名称"""
    displays = {
        # 招聘流程
        WorkflowStage.JOB_CREATED: "✅ 职位已创建",
        WorkflowStage.CANDIDATES_FOUND: "🔍 候选人已找到",
        WorkflowStage.MATCHING_DONE: "🎯 匹配完成",
        WorkflowStage.INTERVIEW_SCHEDULED: "📅 面试已安排",
        WorkflowStage.EVALUATION_DONE: "📊 评估完成",
        WorkflowStage.NEGOTIATION_DONE: "🤝 谈判完成",
        WorkflowStage.HIRED: "🎉 已录用",
        WorkflowStage.REJECTED: "❌ 已拒绝",
        # 求职流程
        WorkflowStage.PROFILE_CREATED: "📝 简历已创建",
        WorkflowStage.JOBS_FOUND: "🔍 职位已找到",
        WorkflowStage.APPLIED: "📨 已投递",
        WorkflowStage.INTERVIEW_PASSED: "✅ 面试通过",
        WorkflowStage.OFFER_RECEIVED: "📨 Offer已收到",
        WorkflowStage.OFFER_ACCEPTED: "🎉 Offer已接受",
        WorkflowStage.OFFER_DECLINED: "❌ Offer已拒绝"
    }
    return displays.get(stage, stage)


@router.get("/stages")
async def get_all_stages() -> Dict[str, Any]:
    """获取所有阶段定义"""
    return {
        "recruiter": {
            "name": "招聘流程",
            "forward": [
                {"stage": WorkflowStage.JOB_CREATED, "name": "创建职位", "step": 1},
                {"stage": WorkflowStage.CANDIDATES_FOUND, "name": "搜索候选人", "step": 2},
                {"stage": WorkflowStage.MATCHING_DONE, "name": "匹配", "step": 3},
                {"stage": WorkflowStage.INTERVIEW_SCHEDULED, "name": "面试", "step": 4},
                {"stage": WorkflowStage.EVALUATION_DONE, "name": "评估", "step": 5},
                {"stage": WorkflowStage.NEGOTIATION_DONE, "name": "谈判", "step": 6},
                {"stage": WorkflowStage.HIRED, "name": "录用", "step": 7}
            ],
            "backward": [
                {"stage": WorkflowStage.REJECTED, "name": "拒绝候选人", "action": "reject"}
            ]
        },
        "candidate": {
            "name": "求职流程",
            "forward": [
                {"stage": WorkflowStage.PROFILE_CREATED, "name": "创建简历", "step": 1},
                {"stage": WorkflowStage.JOBS_FOUND, "name": "搜索职位", "step": 2},
                {"stage": WorkflowStage.APPLIED, "name": "投递", "step": 3},
                {"stage": WorkflowStage.INTERVIEW_PASSED, "name": "面试", "step": 4},
                {"stage": WorkflowStage.OFFER_RECEIVED, "name": "收到Offer", "step": 5},
                {"stage": WorkflowStage.OFFER_ACCEPTED, "name": "接受Offer", "step": 6}
            ],
            "backward": [
                {"stage": WorkflowStage.OFFER_DECLINED, "name": "拒绝Offer", "action": "decline"}
            ]
        }
    }