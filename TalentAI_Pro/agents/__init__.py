"""
Agents Package

招聘生态中的 AI Agent 集合
"""

from .interview import (
    InterviewAgent,
    InterviewState,
    QuestionGenerator,
    EvaluationEngine,
    ReportGenerator,
    InterviewSession,
    InterviewSessionManager,
    generate_interview_questions,
    evaluate_answer,
    generate_report,
    EVALUATION_DIMENSIONS,
    RECOMMENDATION_LEVELS
)

__all__ = [
    "InterviewAgent",
    "InterviewState",
    "QuestionGenerator",
    "EvaluationEngine",
    "ReportGenerator",
    "InterviewSession",
    "InterviewSessionManager",
    "generate_interview_questions",
    "evaluate_answer",
    "generate_report",
    "EVALUATION_DIMENSIONS",
    "RECOMMENDATION_LEVELS",
]

# Agent 类型枚举
class AgentType:
    """Agent 类型"""
    INTERVIEW = "interview"
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"
    COORDINATOR = "coordinator"