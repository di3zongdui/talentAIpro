"""
API v2 - Agent信任与通信协议
基于第一性原理设计的Agent信任架构
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid
import json

router = APIRouter(prefix="/api/v2")


# ========== Enums ==========

class AgentType(str, Enum):
    RECRUITER = "recruiter"      # 招聘Agent
    CANDIDATE = "candidate"      # 候选人Agent
    INTERVIEWER = "interviewer"  # 面试Agent
    ENTERPRISE = "enterprise"    # 企业Agent


class DisclosureLevel(str, Enum):
    PUBLIC = "public"                    # 公开
    MATCHED_ONLY = "matched_only"        # 匹配后可见
    OFFER_ONLY = "offer_only"           # Offer阶段可见
    NEVER = "never"                     # 永不披露


class IntentType(str, Enum):
    # 候选人Agent → 招聘Agent
    INTEREST_EXPRESSION = "interest_expression"
    RESUME_DISCLOSURE = "resume_disclosure"
    INTERVIEW_ACCEPTANCE = "interview_acceptance"
    OFFER_NEGOTIATION = "offer_negotiation"
    OFFER_ACCEPTANCE = "offer_acceptance"
    OFFER_REJECTION = "offer_rejection"

    # 招聘Agent → 候选人Agent
    JOB_MATCH_NOTIFICATION = "job_match_notification"
    INTERVIEW_INVITATION = "interview_invitation"
    OFFER_EXTENDED = "offer_extended"
    OFFER_UPDATED = "offer_updated"
    OFFER_WITHDRAWN = "offer_withdrawn"


class NegotiationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COUNTER_OFFER = "counter_offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ConstraintViolation(str, Enum):
    NONE = "none"
    SALARY_MIN = "salary_min"
    SALARY_MAX = "salary_max"
    DEALBREAKER_HIT = "dealbreaker_hit"
    ACTION_NOT_AUTHORIZED = "action_not_authorized"


# ========== Models - 代理授权 ==========

class AuthorizationConstraints(BaseModel):
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    max_interview_rounds: Optional[int] = None
    allowed_companies: List[str] = []
    denied_companies: List[str] = []
    denied_locations: List[str] = []
    required_wlb_score: Optional[float] = None


class ProxyAuthorization(BaseModel):
    """代理授权声明"""
    principal_id: str
    principal_type: str  # "individual" | "enterprise"
    agent_id: str
    agent_type: AgentType
    agent_capabilities: List[str]
    authorized_actions: List[str]
    denied_actions: List[str] = []
    constraints: AuthorizationConstraints = AuthorizationConstraints()
    valid_from: datetime
    valid_until: datetime
    auto_renew: bool = False
    revocable: bool = True
    revocation_requires: str = "immediate"  # "immediate" | "24h" | "72h"
    delegate_to_human_on_revoke: List[str] = []


class AuthorizationStatus(BaseModel):
    is_valid: bool
    authorization_id: str
    verified_at: datetime
    verified_claims: Dict[str, Any] = {}


class AgentRegistration(BaseModel):
    agent_id: str
    agent_type: AgentType
    owner_id: str
    owner_type: str  # "individual" | "enterprise"
    capabilities: List[str]
    understood_taxonomies: List[str] = ["talentos_core_v1"]
    communication_protocols: List[str] = ["ws", "http"]
    metadata: Dict[str, Any] = {}


class AgentCertificate(BaseModel):
    certificate_id: str
    agent_id: str
    issued_at: datetime
    expires_at: datetime
    trust_score: float = 0.5
    verified_claims: Dict[str, Any] = {}


# ========== Models - 偏好模型 ==========

class PreferencePriority(BaseModel):
    dimension: str  # "WLB" | "salary" | "location" | "growth" | "culture"
    weight: float = Field(ge=0, le=1)
    description: str = ""


class FlexibilityRange(BaseModel):
    can_flex_to: float = Field(ge=0, le=1)  # 0-1, 可妥协到什么程度
    requires_approval_below: float = Field(ge=0, le=1)  # 需要人类审批的阈值
    never_below: Optional[float] = Field(default=None, ge=0, le=1)  # 绝对底线


class PreferenceFlexibilities(BaseModel):
    salary: FlexibilityRange = FlexibilityRange(can_flex_to=0.8, requires_approval_below=0.7)
    WLB: FlexibilityRange = FlexibilityRange(can_flex_to=0.5, requires_approval_below=0.3, never_below=0.2)
    location: FlexibilityRange = FlexibilityRange(can_flex_to=0.6, requires_approval_below=0.4)


class Dealbreaker(BaseModel):
    type: str  # "company" | "location" | "salary" | "culture" | "role"
    value: Any
    strictness: float = Field(ge=0, le=1)  # 1.0 = 绝对不能妥协


class PreferenceModel(BaseModel):
    """动态偏好模型"""
    model_id: str
    owner_id: str
    owner_type: str  # "individual" | "enterprise"

    priorities: List[PreferencePriority] = []
    flexibilities: PreferenceFlexibilities = PreferenceFlexibilities()
    dealbreakers: List[Dealbreaker] = []

    explicit_feedback_count: int = 0
    implicit_feedback_count: int = 0
    model_version: int = 1
    last_updated: datetime

    # Agent谈判授权
    counter_offer_authority: float = Field(default=0.5, ge=0, le=1)  # Agent还价权限 0-1
    auto_accept_threshold: float = Field(default=0.8, ge=0, le=1)  # 自动接受阈值


class PreferenceFeedback(BaseModel):
    """偏好反馈"""
    model_version: int
    feedback_type: str  # "explicit" | "implicit"
    target_proposal_id: Optional[str] = None
    dimensions: Dict[str, float] = {}  # 维度评分
    overall_score: float = Field(ge=0, le=1)
    comments: str = ""


# ========== Models - 用途绑定披露 ==========

class DisclosureAtom(BaseModel):
    """原子信息单元"""
    atom_id: str
    content_type: str  # "skill_match" | "salary_range" | "experience_years" | "education"
    raw_value: Any
    disclosure_level: DisclosureLevel = DisclosureLevel.MATCHED_ONLY

    # 零知识证明
    proof_type: str = "none"  # "none" | "zksnark" | "range_proof"
    proof: Optional[str] = None

    # 元数据
    created_at: datetime
    owner_id: str


class DisclosureAuthorization(BaseModel):
    """披露授权"""
    authorization_id: str
    atom_id: str
    authorized_recipients: List[str] = []  # Agent IDs
    purpose: str = "recruitment_match"
    valid_until: datetime
    requires_re_approval: bool = False
    approved_at: Optional[datetime] = None


class DisclosureRequest(BaseModel):
    """披露请求"""
    atom_ids: List[str]
    requestor_id: str
    purpose: str
    context: Dict[str, Any] = {}


class DisclosureResponse(BaseModel):
    """披露响应"""
    approved_atoms: List[DisclosureAtom] = []
    pending_atoms: List[str] = []  # atom_ids
    denied_atoms: List[str] = []  # atom_ids
    requires_human_approval: bool = False


# ========== Models - 语义共识 ==========

class SkillLevel(BaseModel):
    beginner: str = "1年以内实际项目经验"
    intermediate: str = "1-3年实际项目经验"
    advanced: str = "3-5年实际项目经验"
    expert: str = "5年以上或开源贡献"


class TaxonomySkill(BaseModel):
    definition: str
    levels: SkillLevel = SkillLevel()
    related_skills: List[str] = []


class TaxonomyDefinition(BaseModel):
    """概念分类体系"""
    version: str = "talentos_core_v1"
    skills: Dict[str, TaxonomySkill] = {}
    experience_equivalence: Dict[str, Any] = {}
    salary_benchmarks: Dict[str, Any] = {}


class AgentSelfDescription(BaseModel):
    """Agent自我描述"""
    agent_id: str
    agent_type: AgentType
    capabilities: List[str]
    understood_taxonomies: List[str]
    communication_protocols: List[str]
    trust_score: float
    verified_by_platform: bool = False
    last_verified: Optional[datetime] = None


# ========== Models - 谈判 ==========

class NegotiationProposal(BaseModel):
    """谈判提案"""
    proposal_id: str
    negotiation_id: str
    from_agent_id: str
    to_agent_id: str
    content: Dict[str, Any]  # 薪资、福利、条件等
    match_score: float = Field(ge=0, le=1)
    generated_at: datetime
    expires_at: Optional[datetime] = None


class NegotiationSession(BaseModel):
    """谈判会话"""
    negotiation_id: str
    job_id: str
    candidate_agent_id: str
    recruiter_agent_id: str

    candidate_preferences_version: int
    recruiter_preferences_version: int

    status: NegotiationStatus = NegotiationStatus.PENDING
    current_round: int = 0
    last_proposal: Optional[NegotiationProposal] = None
    proposals_history: List[NegotiationProposal] = []

    constraint_violations: List[ConstraintViolation] = []
    requires_human_approval: bool = False
    approval_requested_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime


# ========== Models - Agent通信 ==========

class AgentMessage(BaseModel):
    """Agent间消息"""
    message_id: str
    from_agent: str
    to_agent: str
    intent: IntentType
    content: Dict[str, Any]

    # 语义层元数据
    semantic_metadata: Dict[str, Any] = {
        "taxonomy_version": "talentos_core_v1",
        "concept_mappings": {}
    }

    # 授权上下文
    authorization_context: Dict[str, Any] = {
        "authorization_chain_id": None,
        "disclosed_atoms": []
    }

    timestamp: datetime
    requires_response: bool = True
    expires_at: Optional[datetime] = None


class AgentEvent(BaseModel):
    """Agent事件"""
    event_id: str
    event_type: str
    source_agent: str
    target_agent: Optional[str] = None
    data: Dict[str, Any] = {}
    timestamp: datetime


# ========== Models - 响应 ==========

class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentRegistrationResponse(BaseModel):
    success: bool
    certificate: Optional[AgentCertificate] = None
    error: Optional[str] = None


class AuthorizationResponse(BaseModel):
    success: bool
    authorization_chain_id: Optional[str] = None
    status: Optional[AuthorizationStatus] = None
    error: Optional[str] = None


class NegotiationResponse(BaseModel):
    success: bool
    negotiation: Optional[NegotiationSession] = None
    proposal: Optional[NegotiationProposal] = None
    requires_human_approval: bool = False
    approval_reason: Optional[str] = None
    error: Optional[str] = None


# ========== 内存存储 ==========

_agents_db: Dict[str, AgentRegistration] = {}
_certificates_db: Dict[str, AgentCertificate] = {}
_authorizations_db: Dict[str, ProxyAuthorization] = {}
_preference_models_db: Dict[str, PreferenceModel] = {}
_atoms_db: Dict[str, DisclosureAtom] = {}
_negotiations_db: Dict[str, NegotiationSession] = {}
_messages_db: List[AgentMessage] = []

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[agent_id] = websocket

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]

    async def send_to_agent(self, agent_id: str, message: dict):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_json(message)

    async def broadcast(self, message: dict, exclude: List[str] = []):
        for agent_id, ws in self.active_connections.items():
            if agent_id not in exclude:
                await ws.send_json(message)


manager = ConnectionManager()


# ========== API Endpoints ==========

# ---------- Agent注册与认证 ----------

@router.post("/agents/register", response_model=AgentRegistrationResponse)
async def register_agent(registration: AgentRegistration):
    """注册Agent"""
    agent_id = registration.agent_id

    if agent_id in _agents_db:
        return AgentRegistrationResponse(
            success=False,
            error="Agent already registered"
        )

    _agents_db[agent_id] = registration

    # 发放证书
    certificate = AgentCertificate(
        certificate_id=f"CERT-{uuid.uuid4().hex[:12]}",
        agent_id=agent_id,
        issued_at=datetime.now(),
        expires_at=datetime.now(),
        trust_score=0.5,
        verified_claims={"registered_at": datetime.now().isoformat()}
    )
    _certificates_db[agent_id] = certificate

    return AgentRegistrationResponse(success=True, certificate=certificate)


@router.get("/agents/{agent_id}", response_model=ApiResponse)
async def get_agent(agent_id: str):
    """获取Agent信息"""
    if agent_id not in _agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = _agents_db[agent_id]
    certificate = _certificates_db.get(agent_id)

    return ApiResponse(success=True, data={
        "agent": agent,
        "certificate": certificate
    })


@router.get("/agents/{agent_id}/self-description", response_model=ApiResponse)
async def get_agent_self_description(agent_id: str):
    """获取Agent自我描述"""
    if agent_id not in _agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = _agents_db[agent_id]
    cert = _certificates_db.get(agent_id)

    description = AgentSelfDescription(
        agent_id=agent_id,
        agent_type=agent.agent_type,
        capabilities=agent.capabilities,
        understood_taxonomies=agent.understood_taxonomies,
        communication_protocols=agent.communication_protocols,
        trust_score=cert.trust_score if cert else 0.5,
        verified_by_platform=cert is not None,
        last_verified=cert.issued_at if cert else None
    )

    return ApiResponse(success=True, data=description)


# ---------- 代理授权 ----------

@router.post("/agents/{agent_id}/authorize", response_model=AuthorizationResponse)
async def authorize_agent(agent_id: str, authorization: ProxyAuthorization):
    """为Agent创建授权"""
    if agent_id not in _agents_db:
        return AuthorizationResponse(success=False, error="Agent not registered")

    authorization_chain_id = f"AUTH-{uuid.uuid4().hex[:12]}"
    _authorizations_db[authorization_chain_id] = authorization

    status = AuthorizationStatus(
        is_valid=True,
        authorization_id=authorization_chain_id,
        verified_at=datetime.now(),
        verified_claims={"principal_verified": True}
    )

    return AuthorizationResponse(
        success=True,
        authorization_chain_id=authorization_chain_id,
        status=status
    )


@router.get("/agents/{agent_id}/authorization", response_model=ApiResponse)
async def get_authorization(agent_id: str):
    """获取Agent的当前授权状态"""
    authorizations = [
        auth for auth in _authorizations_db.values()
        if auth.agent_id == agent_id
    ]

    valid_auths = [
        auth for auth in authorizations
        if auth.valid_from <= datetime.now() <= auth.valid_until
    ]

    return ApiResponse(success=True, data={
        "authorizations": valid_auths,
        "count": len(valid_auths)
    })


@router.post("/agents/{agent_id}/revoke", response_model=ApiResponse)
async def revoke_agent_authorization(agent_id: str, reason: str = ""):
    """撤销Agent授权"""
    revoked = []
    for auth_id, auth in _authorizations_db.items():
        if auth.agent_id == agent_id:
            auth.revocable = True
            revoked.append(auth_id)

    return ApiResponse(
        success=True,
        data={"revoked_count": len(revoked), "reason": reason}
    )


# ---------- 偏好模型 ----------

@router.post("/preferences/model", response_model=ApiResponse)
async def create_preference_model(preferences: PreferenceModel):
    """创建偏好模型"""
    model_id = preferences.model_id
    _preference_models_db[model_id] = preferences

    return ApiResponse(
        success=True,
        data={"model_id": model_id, "version": preferences.model_version}
    )


@router.get("/preferences/{owner_id}/model", response_model=ApiResponse)
async def get_preference_model(owner_id: str):
    """获取偏好模型"""
    models = [
        m for m in _preference_models_db.values()
        if m.owner_id == owner_id
    ]

    if not models:
        raise HTTPException(status_code=404, detail="Preference model not found")

    latest = max(models, key=lambda x: x.model_version)

    return ApiResponse(success=True, data=latest)


@router.post("/preferences/model/{model_id}/feedback", response_model=ApiResponse)
async def submit_preference_feedback(model_id: str, feedback: PreferenceFeedback):
    """提交偏好反馈"""
    if model_id not in _preference_models_db:
        raise HTTPException(status_code=404, detail="Model not found")

    model = _preference_models_db[model_id]

    # 更新反馈计数
    if feedback.feedback_type == "explicit":
        model.explicit_feedback_count += 1
    else:
        model.implicit_feedback_count += 1

    # 更新维度权重（简单加权平均）
    for dim, score in feedback.dimensions.items():
        for priority in model.priorities:
            if priority.dimension == dim:
                # 简单更新：新旧权重平均
                priority.weight = (priority.weight + score) / 2

    model.model_version += 1
    model.last_updated = datetime.now()

    return ApiResponse(
        success=True,
        data={"model_id": model_id, "new_version": model.model_version}
    )


@router.post("/preferences/model/{model_id}/evaluate", response_model=ApiResponse)
async def evaluate_proposal(model_id: str, proposal: Dict[str, Any]):
    """评估提案是否符合偏好"""
    if model_id not in _preference_models_db:
        raise HTTPException(status_code=404, detail="Model not found")

    model = _preference_models_db[model_id]

    # 计算匹配度
    match_score = 0.8  # 默认分数

    # 检查硬性约束（dealbreakers）
    violations = []
    for dealbreaker in model.dealbreakers:
        if dealbreaker.type in proposal and proposal[dealbreaker.type] == dealbreaker.value:
            violations.append(ConstraintViolation.DEALBREAKER_HIT)
            match_score *= (1 - dealbreaker.strictness)

    # 检查薪资约束
    if "salary" in proposal and model.flexibilities.salary.never_below:
        salary_score = proposal["salary"] / 100000  # 简化计算
        if salary_score < model.flexibilities.salary.never_below:
            violations.append(ConstraintViolation.SALARY_MIN)

    # 是否需要人类审批
    requires_approval = (
        len(violations) > 0 or
        match_score < model.auto_accept_threshold
    )

    return ApiResponse(success=True, data={
        "match_score": match_score,
        "violations": violations,
        "requires_human_approval": requires_approval,
        "auto_decision": "accept" if match_score > 0.9 and not violations else "reject" if match_score < 0.3 else "negotiate"
    })


# ---------- 用途绑定披露 ----------

@router.post("/disclosure/atoms", response_model=ApiResponse)
async def create_disclosure_atom(atom: DisclosureAtom):
    """创建原子披露"""
    atom_id = atom.atom_id
    _atoms_db[atom_id] = atom

    return ApiResponse(success=True, data={"atom_id": atom_id})


@router.get("/disclosure/atoms/{atom_id}", response_model=ApiResponse)
async def get_disclosure_atom(atom_id: str, requestor_id: str = "", purpose: str = ""):
    """获取原子披露（根据授权决定是否可见）"""
    if atom_id not in _atoms_db:
        raise HTTPException(status_code=404, detail="Atom not found")

    atom = _atoms_db[atom_id]

    # 检查披露级别
    if atom.disclosure_level == DisclosureLevel.NEVER:
        return ApiResponse(success=False, error="Atom never disclosed")

    # 根据披露级别和请求者决定是否可见
    can_view = False
    if atom.disclosure_level == DisclosureLevel.PUBLIC:
        can_view = True
    elif atom.disclosure_level == DisclosureLevel.MATCHED_ONLY:
        can_view = purpose in ["match_notification", "interview_invitation"]
    elif atom.disclosure_level == DisclosureLevel.OFFER_ONLY:
        can_view = purpose in ["offer_extended", "offer_negotiation"]

    if not can_view:
        return ApiResponse(success=False, error="Atom not authorized for this purpose")

    return ApiResponse(success=True, data=atom)


@router.post("/disclosure/request", response_model=ApiResponse)
async def request_disclosure(request: DisclosureRequest):
    """批量请求披露"""
    approved = []
    pending = []
    denied = []

    for atom_id in request.atom_ids:
        if atom_id not in _atoms_db:
            denied.append(atom_id)
            continue

        atom = _atoms_db[atom_id]

        # 检查授权
        if atom.disclosure_level == DisclosureLevel.NEVER:
            denied.append(atom_id)
        elif atom.owner_id == request.requestor_id:
            approved.append(atom)  # 自己可以看自己的
        else:
            # 需要授权检查
            if atom.disclosure_level == DisclosureLevel.PUBLIC:
                approved.append(atom)
            else:
                pending.append(atom_id)

    response = DisclosureResponse(
        approved_atoms=approved,
        pending_atoms=pending,
        denied_atoms=denied,
        requires_human_approval=len(pending) > 0
    )

    return ApiResponse(success=True, data=response)


# ---------- 语义共识 ----------

@router.get("/semantics/taxonomy", response_model=ApiResponse)
async def get_taxonomy():
    """获取概念分类体系"""
    taxonomy = TaxonomyDefinition(
        version="talentos_core_v1",
        skills={
            "Python": TaxonomySkill(
                definition="掌握Python编程语言及相关生态",
                levels=SkillLevel(),
                related_skills=["Django", "FastAPI", "pandas"]
            ),
            "JavaScript": TaxonomySkill(
                definition="掌握JavaScript编程语言及相关生态",
                levels=SkillLevel(),
                related_skills=["React", "Vue", "Node.js"]
            ),
            "Machine Learning": TaxonomySkill(
                definition="机器学习理论及实践",
                levels=SkillLevel(),
                related_skills=["TensorFlow", "PyTorch", "scikit-learn"]
            ),
        },
        experience_equivalence={
            "5_years": {
                "definition": "60个月全职实际工作经验",
                "exclude": ["实习", "兼职", "培训"],
                "equivalence": {"part_time": 0.5, "contractor": 0.7}
            }
        },
        salary_benchmarks={
            "CN_SENIOR_SWE": {"min": 400000, "max": 800000, "currency": "CNY"},
            "US_SENIOR_SWE": {"min": 150000, "max": 300000, "currency": "USD"},
        }
    )

    return ApiResponse(success=True, data=taxonomy)


@router.post("/semantics/translate", response_model=ApiResponse)
async def translate_concepts(text: str, source_taxonomy: str, target_taxonomy: str):
    """翻译概念（跨Taxonomy映射）"""
    # 简化实现：实际应用中需要更复杂的语义映射
    return ApiResponse(success=True, data={
        "original": text,
        "source": source_taxonomy,
        "target": target_taxonomy,
        "translated": text,
        "confidence": 0.85
    })


# ---------- 谈判协议 ----------

@router.post("/negotiations/start", response_model=NegotiationResponse)
async def start_negotiation(
    job_id: str,
    candidate_agent_id: str,
    recruiter_agent_id: str
):
    """开始谈判会话"""
    negotiation_id = f"NEG-{uuid.uuid4().hex[:12]}"

    # 获取偏好模型
    candidate_models = [m for m in _preference_models_db.values() if m.owner_id == candidate_agent_id]
    recruiter_models = [m for m in _preference_models_db.values() if m.owner_id == recruiter_agent_id]

    if not candidate_models or not recruiter_models:
        return NegotiationResponse(
            success=False,
            error="Preference models not found for both parties"
        )

    candidate_pref = max(candidate_models, key=lambda x: x.model_version)
    recruiter_pref = max(recruiter_models, key=lambda x: x.model_version)

    negotiation = NegotiationSession(
        negotiation_id=negotiation_id,
        job_id=job_id,
        candidate_agent_id=candidate_agent_id,
        recruiter_agent_id=recruiter_agent_id,
        candidate_preferences_version=candidate_pref.model_version,
        recruiter_preferences_version=recruiter_pref.model_version,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    _negotiations_db[negotiation_id] = negotiation

    return NegotiationResponse(success=True, negotiation=negotiation)


@router.post("/negotiations/{negotiation_id}/propose", response_model=NegotiationResponse)
async def create_proposal(negotiation_id: str, proposal: NegotiationProposal):
    """创建提案"""
    if negotiation_id not in _negotiations_db:
        return NegotiationResponse(success=False, error="Negotiation not found")

    negotiation = _negotiations_db[negotiation_id]
    negotiation.current_round += 1
    negotiation.last_proposal = proposal
    negotiation.updated_at = datetime.now()

    # 评估提案
    candidate_pref = None
    for m in _preference_models_db.values():
        if m.owner_id == negotiation.candidate_agent_id:
            candidate_pref = m
            break

    if candidate_pref:
        violations = []
        match_score = 0.8

        for dealbreaker in candidate_pref.dealbreakers:
            if dealbreaker.type in proposal.content:
                violations.append(ConstraintViolation.DEALBREAKER_HIT)

        requires_approval = (
            len(violations) > 0 or
            proposal.match_score < candidate_pref.auto_accept_threshold
        )

        negotiation.requires_human_approval = requires_approval
        negotiation.constraint_violations = violations

        if requires_approval:
            negotiation.approval_requested_at = datetime.now()

    return NegotiationResponse(
        success=True,
        negotiation=negotiation,
        proposal=proposal,
        requires_human_approval=negotiation.requires_human_approval
    )


@router.post("/negotiations/{negotiation_id}/approve", response_model=NegotiationResponse)
async def approve_negotiation(
    negotiation_id: str,
    decision: str,  # "accept" | "reject" | "counter"
    counter_content: Optional[Dict[str, Any]] = None
):
    """人类审批谈判决策"""
    if negotiation_id not in _negotiations_db:
        return NegotiationResponse(success=False, error="Negotiation not found")

    negotiation = _negotiations_db[negotiation_id]

    if decision == "accept":
        negotiation.status = NegotiationStatus.ACCEPTED
        return NegotiationResponse(success=True, negotiation=negotiation)
    elif decision == "reject":
        negotiation.status = NegotiationStatus.REJECTED
        return NegotiationResponse(success=True, negotiation=negotiation)
    else:
        # counter - 创建反提案
        counter_proposal = NegotiationProposal(
            proposal_id=f"PROP-{uuid.uuid4().hex[:12]}",
            negotiation_id=negotiation_id,
            from_agent=negotiation.recruiter_agent_id,
            to_agent=negotiation.candidate_agent_id,
            content=counter_content or {},
            match_score=0.8,
            generated_at=datetime.now()
        )
        negotiation.current_round += 1
        negotiation.last_proposal = counter_proposal
        negotiation.status = NegotiationStatus.COUNTER_OFFER

        return NegotiationResponse(
            success=True,
            negotiation=negotiation,
            proposal=counter_proposal
        )


# ---------- Agent间通信 ----------

@router.get("/messages/inbox/{agent_id}", response_model=ApiResponse)
async def get_messages(agent_id: str, unread_only: bool = False):
    """获取Agent的消息"""
    messages = [
        m for m in _messages_db
        if m.to_agent == agent_id
    ]

    if unread_only:
        # 简化：假设所有未读的都在队列中
        pass

    return ApiResponse(success=True, data={
        "messages": messages[-50:],  # 最近50条
        "count": len(messages)
    })


@router.post("/messages/send", response_model=ApiResponse)
async def send_message(message: AgentMessage):
    """发送消息（通过HTTP）"""
    message.message_id = f"MSG-{uuid.uuid4().hex[:12]}"
    message.timestamp = datetime.now()
    _messages_db.append(message)

    # 如果目标Agent在线，通过WebSocket推送
    await manager.send_to_agent(message.to_agent, {
        "type": "message",
        "data": message
    })

    return ApiResponse(success=True, data={"message_id": message.message_id})


# ---------- WebSocket端点 ----------

@router.websocket("/ws/agents")
async def websocket_endpoint(websocket: WebSocket):
    """Agent WebSocket连接端点"""
    # 简化：实际需要认证
    await websocket.accept()

    agent_id = None
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "auth":
                agent_id = data.get("agent_id")
                await manager.send_to_agent(agent_id, {
                    "type": "auth_success",
                    "agent_id": agent_id
                })

            elif data.get("type") == "message":
                # 转发消息
                to_agent = data.get("to_agent")
                await manager.send_to_agent(to_agent, {
                    "type": "message",
                    "from_agent": agent_id,
                    "data": data.get("content", {})
                })

            elif data.get("type") == "subscribe":
                # 订阅事件
                event_type = data.get("event_type")
                # 实现订阅逻辑
                pass

    except WebSocketDisconnect:
        if agent_id:
            manager.disconnect(agent_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if agent_id:
            manager.disconnect(agent_id)


# ---------- 事件系统 ----------

@router.get("/events", response_model=ApiResponse)
async def get_events(
    agent_id: str,
    event_type: Optional[str] = None,
    limit: int = 50
):
    """获取Agent的事件"""
    # 简化实现
    return ApiResponse(success=True, data={
        "events": [],
        "count": 0
    })


@router.post("/events/publish", response_model=ApiResponse)
async def publish_event(event: AgentEvent):
    """发布事件"""
    event.event_id = f"EVENT-{uuid.uuid4().hex[:12]}"
    event.timestamp = datetime.now()

    # 通过WebSocket广播
    await manager.broadcast({
        "type": "event",
        "data": event
    }, exclude=[event.source_agent])

    return ApiResponse(success=True, data={"event_id": event.event_id})
