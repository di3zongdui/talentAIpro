"""
Interview Agent API Endpoints

Interview Agent 的 FastAPI 端点
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..interview.question_generator import QuestionGenerator
from ..interview.evaluation_engine import EvaluationEngine
from ..interview.report_generator import ReportGenerator
from ..interview.interview_session import (
    InterviewSession, InterviewSessionManager, InterviewType,
    get_session_manager
)

router = APIRouter(prefix="/api/v2/interviews", tags=["Interview Agent"])

# Request/Response Models

class GenerateQuestionsRequest(BaseModel):
    """生成问题请求"""
    job_description: Dict[str, Any] = Field(..., description="JD解析结果")
    candidate_profile: Dict[str, Any] = Field(..., description="候选人背景")
    interview_type: str = Field(default="technical", description="面试类型")
    candidate_id: str = Field(..., description="候选人ID")
    candidate_name: str = Field(..., description="候选人姓名")
    job_id: str = Field(..., description="职位ID")
    job_title: str = Field(..., description="职位名称")


class SubmitAnswerRequest(BaseModel):
    """提交回答请求"""
    question_id: str = Field(..., description="问题ID")
    answer: str = Field(..., description="候选人回答")


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    interview_type: str = "technical"


# API Endpoints

@router.post("/generate-questions")
async def generate_questions(request: GenerateQuestionsRequest):
    """
    生成面试问题

    根据JD和候选人背景生成结构化面试问题
    """
    try:
        generator = QuestionGenerator()
        questions = generator.generate(
            job_description=request.job_description,
            candidate_profile=request.candidate_profile
        )

        # 创建会话
        manager = get_session_manager()
        interview_type = InterviewType(request.interview_type)
        session = manager.create_session(
            candidate_id=request.candidate_id,
            candidate_name=request.candidate_name,
            job_id=request.job_id,
            job_title=request.job_title,
            interview_type=interview_type
        )

        # 设置问题
        manager.set_questions(session.session_id, questions)

        return {
            "success": True,
            "session_id": session.session_id,
            "interview_id": questions.interview_id,
            "questions": questions.to_dict(),
            "duration_minutes": questions.duration_minutes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    """创建面试会话（不生成问题）"""
    try:
        manager = get_session_manager()
        interview_type = InterviewType(request.interview_type)
        session = manager.create_session(
            candidate_id=request.candidate_id,
            candidate_name=request.candidate_name,
            job_id=request.job_id,
            job_title=request.job_title,
            interview_type=interview_type
        )

        return {
            "success": True,
            "session_id": session.session_id,
            "state": session.state.value,
            "created_at": session.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """获取面试会话状态"""
    manager = get_session_manager()
    session = manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "success": True,
        "session": session.to_dict()
    }


@router.get("/sessions/{session_id}/progress")
async def get_progress(session_id: str):
    """获取面试进度"""
    manager = get_session_manager()
    progress = manager.get_progress(session_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "success": True,
        "progress": progress
    }


@router.get("/sessions/{session_id}/current-question")
async def get_current_question(session_id: str):
    """获取当前问题"""
    manager = get_session_manager()
    question = manager.get_current_question(session_id)

    if question is None:
        # 面试已完成或问题已全部回答
        session = manager.get_session(session_id)
        if session and session.state.value == "completed":
            return {
                "success": True,
                "completed": True,
                "message": "面试已完成"
            }
        raise HTTPException(status_code=404, detail="No more questions")

    return {
        "success": True,
        "question": question,
        "answered": len(session.answers) if session.answers else 0,
        "total": session.questions.total_questions if session.questions else 0
    }


@router.post("/sessions/{session_id}/start")
async def start_interview(session_id: str):
    """开始面试"""
    try:
        manager = get_session_manager()
        session = manager.start_interview(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "state": session.state.value,
            "started_at": session.started_at,
            "first_question": manager.get_current_question(session_id)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/submit")
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    """提交回答"""
    try:
        manager = get_session_manager()
        result = manager.submit_answer(
            session_id=session_id,
            question_id=request.question_id,
            answer=request.answer
        )

        # 检查是否所有问题都已回答
        session = manager.get_session(session_id)
        all_answered = (
            session.current_question_index >=
            (session.questions.total_questions if session.questions else 0)
        )

        return {
            "success": True,
            **result,
            "all_answered": all_answered
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/complete")
async def complete_interview(session_id: str):
    """完成面试并生成报告"""
    try:
        manager = get_session_manager()
        report = manager.complete_interview(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "state": "completed",
            "report": report.to_dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/report")
async def get_report(session_id: str):
    """获取面试报告"""
    manager = get_session_manager()
    session = manager.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.report:
        raise HTTPException(status_code=400, detail="Interview not completed")

    return {
        "success": True,
        "report": session.report.to_dict(),
        "markdown": session.report.to_markdown()
    }


@router.post("/sessions/{session_id}/cancel")
async def cancel_interview(session_id: str, reason: str = ""):
    """取消面试"""
    try:
        manager = get_session_manager()
        session = manager.cancel_interview(session_id, reason)

        return {
            "success": True,
            "session_id": session_id,
            "state": session.state.value,
            "reason": reason
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/active")
async def list_active_sessions():
    """列出所有活跃会话"""
    manager = get_session_manager()
    sessions = manager.list_active_sessions()

    return {
        "success": True,
        "count": len(sessions),
        "sessions": sessions
    }


# 评估相关端点

@router.post("/evaluate-answer")
async def evaluate_answer(question: Dict[str, Any], answer: str):
    """
    评估单个回答

    不创建会话，直接评估回答
    """
    try:
        engine = EvaluationEngine()
        result = engine.evaluate_answer(question, answer)

        return {
            "success": True,
            "evaluation": result.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 健康检查

@router.get("/health")
async def health_check():
    """健康检查"""
    manager = get_session_manager()
    return {
        "status": "healthy",
        "active_sessions": len(manager.list_active_sessions()),
        "total_sessions": len(manager.sessions)
    }