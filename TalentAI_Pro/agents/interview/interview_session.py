"""
Interview Session - 面试会话管理

管理完整面试流程的状态和状态转换
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json


class InterviewState:
    """面试状态枚举"""
    CREATED = "created"
    QUESTIONS_GENERATED = "questions_generated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewType(Enum):
    """面试类型"""
    TECHNICAL = "technical"           # 技术面试
    BEHAVIORAL = "behavioral"        # 行为面试
    FINAL = "final"                  # 终面
    SCREENING = "screening"          # 初筛


@dataclass
class InterviewSession:
    """
    面试会话

    管理完整面试流程的状态和数据
    """
    session_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    interview_type: InterviewType

    # 状态
    state: InterviewState = InterviewState.CREATED

    # 问题
    questions: Optional['StructuredQuestions'] = None
    current_question_index: int = 0

    # 回答
    answers: Dict[str, str] = field(default_factory=dict)  # question_id -> answer

    # 评估
    evaluations: List['QuestionEvaluation'] = field(default_factory=list)
    final_evaluation: Optional['InterviewEvaluation'] = None

    # 报告
    report: Optional['InterviewReport'] = None

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # 回调
    on_state_change: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "job_id": self.job_id,
            "job_title": self.job_title,
            "interview_type": self.interview_type.value,
            "state": self.state.value,
            "questions": self.questions.to_dict() if self.questions else None,
            "current_question_index": self.current_question_index,
            "answers": self.answers,
            "total_questions": self.questions.total_questions if self.questions else 0,
            "answered_questions": len(self.answers),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class InterviewSessionManager:
    """
    面试会话管理器

    管理多个面试会话，支持创建、恢复、完成等操作
    """

    def __init__(self):
        self.sessions: Dict[str, InterviewSession] = {}
        self.candidate_sessions: Dict[str, List[str]] = {}  # candidate_id -> session_ids
        self.evaluation_engine = EvaluationEngine()
        self.report_generator = ReportGenerator()

    def create_session(
        self,
        candidate_id: str,
        candidate_name: str,
        job_id: str,
        job_title: str,
        interview_type: InterviewType = InterviewType.TECHNICAL
    ) -> InterviewSession:
        """创建新面试会话"""
        session_id = str(uuid.uuid4())

        session = InterviewSession(
            session_id=session_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            job_id=job_id,
            job_title=job_title,
            interview_type=interview_type
        )

        self.sessions[session_id] = session

        # 记录候选人会话
        if candidate_id not in self.candidate_sessions:
            self.candidate_sessions[candidate_id] = []
        self.candidate_sessions[candidate_id].append(session_id)

        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """获取会话"""
        return self.sessions.get(session_id)

    def get_candidate_sessions(self, candidate_id: str) -> List[InterviewSession]:
        """获取候选人的所有会话"""
        session_ids = self.candidate_sessions.get(candidate_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def set_questions(
        self,
        session_id: str,
        questions: 'StructuredQuestions'
    ) -> InterviewSession:
        """设置面试问题"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.questions = questions
        session.state = InterviewState.QUESTIONS_GENERATED

        return session

    def start_interview(self, session_id: str) -> InterviewSession:
        """开始面试"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.state != InterviewState.QUESTIONS_GENERATED:
            raise ValueError(f"Cannot start interview from state: {session.state}")

        session.state = InterviewState.IN_PROGRESS
        session.started_at = datetime.now().isoformat()

        return session

    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        提交回答

        Returns:
            包含评估结果的字典
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.state != InterviewState.IN_PROGRESS:
            raise ValueError(f"Interview not in progress: {session.state}")

        # 记录回答
        session.answers[question_id] = answer

        # 找到对应问题
        question = self._find_question(session, question_id)
        if not question:
            raise ValueError(f"Question not found: {question_id}")

        # 评估回答
        evaluation = self.evaluation_engine.evaluate_answer(
            question.to_dict() if hasattr(question, 'to_dict') else question,
            answer
        )
        session.evaluations.append(evaluation)

        # 更新当前问题索引
        session.current_question_index += 1

        return {
            "question_id": question_id,
            "evaluation": evaluation.to_dict(),
            "session_state": session.state.value,
            "answered": len(session.answers),
            "total": session.questions.total_questions if session.questions else 0
        }

    def _find_question(
        self,
        session: InterviewSession,
        question_id: str
    ):
        """查找问题"""
        if not session.questions:
            return None

        # 技术问题
        for q in session.questions.technical_questions:
            if q.id == question_id:
                return q

        # 行为问题
        for q in session.questions.behavioral_questions:
            if q.id == question_id:
                return q

        return None

    def complete_interview(self, session_id: str) -> 'InterviewReport':
        """完成面试并生成报告"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.state != InterviewState.IN_PROGRESS:
            raise ValueError(f"Interview not in progress: {session.state}")

        # 最终评估
        session.final_evaluation = self.evaluation_engine.evaluate_interview(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            question_evaluations=session.evaluations
        )

        # 生成报告
        session.report = self.report_generator.generate(
            evaluation=session.final_evaluation,
            candidate_name=session.candidate_name,
            job_title=session.job_title
        )

        # 更新状态
        session.state = InterviewState.COMPLETED
        session.completed_at = datetime.now().isoformat()

        return session.report

    def cancel_interview(self, session_id: str, reason: str = "") -> InterviewSession:
        """取消面试"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.state = InterviewState.CANCELLED
        session.completed_at = datetime.now().isoformat()

        return session

    def get_current_question(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取当前问题"""
        session = self.sessions.get(session_id)
        if not session or not session.questions:
            return None

        questions = (
            session.questions.technical_questions +
            session.questions.behavioral_questions
        )

        if session.current_question_index < len(questions):
            return questions[session.current_question_index].to_dict()

        return None

    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """获取面试进度"""
        session = self.sessions.get(session_id)
        if not session:
            return {}

        total = session.questions.total_questions if session.questions else 0
        answered = len(session.answers)

        return {
            "session_id": session_id,
            "state": session.state.value,
            "total_questions": total,
            "answered_questions": answered,
            "progress_percent": round(answered / total * 100, 1) if total > 0 else 0,
            "created_at": session.created_at,
            "started_at": session.started_at,
            "completed_at": session.completed_at
        }

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """列出所有活跃会话"""
        active = [
            s for s in self.sessions.values()
            if s.state in [InterviewState.CREATED, InterviewState.QUESTIONS_GENERATED, InterviewState.IN_PROGRESS]
        ]

        return [s.to_dict() for s in active]


# 全局会话管理器
_session_manager: Optional[InterviewSessionManager] = None


def get_session_manager() -> InterviewSessionManager:
    """获取全局会话管理器"""
    global _session_manager
    if _session_manager is None:
        _session_manager = InterviewSessionManager()
    return _session_manager