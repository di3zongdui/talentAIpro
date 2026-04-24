"""
Base Agent Class
Common functionality for all agents
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class AgentType(Enum):
    """Agent types in the ecosystem"""
    RECRUITER = "recruiter"      # 招聘Agent
    CANDIDATE = "candidate"      # 候选人Agent
    INTERVIEW = "interview"      # 面试Agent
    NEGOTIATION = "negotiation"  # 谈判Agent


class AgentStatus(Enum):
    """Agent lifecycle status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"


class AgentCapability(Enum):
    """Agent capabilities"""
    # Recruiter capabilities
    SEARCH_CANDIDATES = "search_candidates"
    SCREEN_RESUMES = "screen_resumes"
    SCHEDULE_INTERVIEWS = "schedule_interviews"
    MAKE_OFFERS = "make_offers"
    ONBOARD_CANDIDATES = "onboard_candidates"

    # Candidate capabilities
    SEARCH_JOBS = "search_jobs"
    APPLY_JOBS = "apply_jobs"
    PREPARE_INTERVIEWS = "prepare_interviews"
    NEGOTIATE_OFFERS = "negotiate_offers"
    ACCEPT_OFFERS = "accept_offers"

    # Interview capabilities
    GENERATE_QUESTIONS = "generate_questions"
    EVALUATE_ANSWERS = "evaluate_answers"
    GENERATE_REPORTS = "generate_reports"

    # Common
    COMMUNICATE = "communicate"
    LEARN_PREFERENCES = "learn_preferences"
    MAKE_DECISIONS = "make_decisions"


@dataclass
class AgentProfile:
    """Agent profile / identity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: AgentType = AgentType.RECRUITER
    description: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    owner_id: str = ""  # Human owner ID
    owner_name: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    status: AgentStatus = AgentStatus.INACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_capability(self, cap: AgentCapability) -> bool:
        return cap in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "capabilities": [c.value for c in self.capabilities],
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata,
        }


@dataclass
class AgentMessage:
    """Message between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""  # Agent ID
    to_agent: str = ""    # Agent ID or "broadcast"
    content: Dict[str, Any] = field(default_factory=dict)
    message_type: str = "inform"  # inform, request, query, response
    in_reply_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "type": self.message_type,
            "in_reply_to": self.in_reply_to,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ProxyAuthorization:
    """Human authorization for agent actions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    human_id: str = ""
    human_name: str = ""
    authorized_actions: List[str] = field(default_factory=list)  # Action names
    constraints: Dict[str, Any] = field(default_factory=dict)  # e.g., {"min_salary": 30000}
    human_approval_threshold: float = 0.8  # Auto-approve if confidence > threshold
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        if self.revoked:
            return False
        now = datetime.now()
        if self.valid_until and now > self.valid_until:
            return False
        return True

    def can_auto_approve(self, action: str, confidence: float) -> bool:
        if not self.is_valid():
            return False
        if action not in self.authorized_actions:
            return False
        return confidence >= self.human_approval_threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "human_id": self.human_id,
            "human_name": self.human_name,
            "authorized_actions": self.authorized_actions,
            "constraints": self.constraints,
            "approval_threshold": self.human_approval_threshold,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "revoked": self.revoked,
        }


@dataclass
class AgentDecision:
    """Agent decision record for transparency"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    action: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    confidence: float = 0.0
    auto_approved: bool = False
    human_approved: Optional[bool] = None
    human_approver: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    decided_at: Optional[datetime] = None

    def approve(self, approver_id: str):
        self.human_approved = True
        self.human_approver = approver_id
        self.decided_at = datetime.now()

    def reject(self, approver_id: str, reason: str = ""):
        self.human_approved = False
        self.human_approver = approver_id
        self.decided_at = datetime.now()
        if reason:
            self.context["rejection_reason"] = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "action": self.action,
            "context": self.context,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "auto_approved": self.auto_approved,
            "human_approved": self.human_approved,
            "human_approver": self.human_approver,
            "created_at": self.created_at.isoformat(),
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
        }


class Agent:
    """Base Agent class"""

    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.authorization: Optional[ProxyAuthorization] = None
        self.decision_history: List[AgentDecision] = []

    @property
    def id(self) -> str:
        return self.profile.id

    @property
    def name(self) -> str:
        return self.profile.name

    @property
    def type(self) -> AgentType:
        return self.profile.type

    def set_authorization(self, auth: ProxyAuthorization):
        self.authorization = auth

    def revoke_authorization(self):
        if self.authorization:
            self.authorization.revoked = True
            self.authorization.revoked_at = datetime.now()

    def is_authorized_for(self, action: str) -> bool:
        if not self.authorization or not self.authorization.is_valid():
            return False
        return action in self.authorization.authorized_actions

    def can_auto_decide(self, action: str, confidence: float) -> bool:
        if not self.is_authorized_for(action):
            return False
        return self.authorization.can_auto_approve(action, confidence)

    def record_decision(self, decision: AgentDecision):
        self.decision_history.append(decision)

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message, return response"""
        raise NotImplementedError("Subclasses must implement process_message")

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action with the given parameters"""
        raise NotImplementedError("Subclasses must implement execute_action")

    def get_capabilities(self) -> List[AgentCapability]:
        return self.profile.capabilities

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "authorization": self.authorization.to_dict() if self.authorization else None,
            "recent_decisions": [d.to_dict() for d in self.decision_history[-10:]],
        }
