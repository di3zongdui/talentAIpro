# TalentAI Pro - Agent API v2 文档

## 概述

Agent API v2 是基于**第一性原理**设计的Agent信任与通信协议，旨在解决：

> **人类如何信任Agent替自己做出重要招聘决策？**

## 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    TalentAI Pro Agent Network                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────┐     ┌─────────────────────────────────────┐   │
│   │ Recruiter   │     │         TalentAI Pro API v2          │   │
│   │   Agent     │←───→│                                      │   │
│   └─────────────┘     │  ┌────────────────────────────────┐  │   │
│                       │  │     Agent Trust Layer          │  │   │
│   ┌─────────────┐     │  │  • 代理授权 (Proxy Auth)       │  │   │
│   │ Candidate   │←───→│  │  • 偏好模型 (Preference)      │  │   │
│   │   Agent     │     │  │  • 用途披露 (Disclosure)      │  │   │
│   └─────────────┘     │  │  • 语义共识 (Semantics)       │  │   │
│                       │  └────────────────────────────────┘  │   │
│   ┌─────────────┐     │                                      │   │
│   │ Interviewer │     │  ┌────────────────────────────────┐  │   │
│   │   Agent     │←───→│  │   Negotiation Protocol         │  │   │
│   └─────────────┘     │  │  • 谈判会话                    │  │   │
│                       │  │  • 提案生成                    │  │   │
│                       │  │  • 人类审批                    │  │   │
│                       │  └────────────────────────────────┘  │   │
│                       └─────────────────────────────────────┘   │
│                                     │                           │
│                                     ▼                           │
│                       ┌─────────────────────────────────────┐   │
│                       │        WebSocket Gateway              │   │
│                       │   ws://localhost:8089/ws/agents     │   │
│                       └─────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## API端点总览

### 1. Agent注册与认证 `/api/v2/agents`

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v2/agents/register` | 注册Agent |
| GET | `/api/v2/agents/{agent_id}` | 获取Agent信息 |
| GET | `/api/v2/agents/{agent_id}/self-description` | 获取Agent自我描述 |
| POST | `/api/v2/agents/{agent_id}/authorize` | 为Agent创建授权 |
| GET | `/api/v2/agents/{agent_id}/authorization` | 获取授权状态 |
| POST | `/api/v2/agents/{agent_id}/revoke` | 撤销授权 |

### 2. 偏好模型 `/api/v2/preferences`

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v2/preferences/model` | 创建偏好模型 |
| GET | `/api/v2/preferences/{owner_id}/model` | 获取偏好模型 |
| POST | `/api/v2/preferences/model/{model_id}/feedback` | 提交偏好反馈 |
| POST | `/api/v2/preferences/model/{model_id}/evaluate` | 评估提案 |

### 3. 用途绑定披露 `/api/v2/disclosure`

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v2/disclosure/atoms` | 创建原子披露 |
| GET | `/api/v2/disclosure/atoms/{atom_id}` | 获取原子披露 |
| POST | `/api/v2/disclosure/request` | 批量请求披露 |

### 4. 语义共识 `/api/v2/semantics`

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/semantics/taxonomy` | 获取概念分类体系 |
| POST | `/api/v2/semantics/translate` | 跨Taxonomy概念翻译 |

### 5. 谈判协议 `/api/v2/negotiations`

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v2/negotiations/start` | 开始谈判会话 |
| POST | `/api/v2/negotiations/{id}/propose` | 创建提案 |
| POST | `/api/v2/negotiations/{id}/approve` | 人类审批 |

### 6. 消息通信 `/api/v2/messages`

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/messages/inbox/{agent_id}` | 获取消息 |
| POST | `/api/v2/messages/send` | 发送消息 |

### 7. 事件系统 `/api/v2/events`

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/events` | 获取事件 |
| POST | `/api/v2/events/publish` | 发布事件 |

### 8. WebSocket `/ws/agents`

| 类型 | 描述 |
|------|------|
| WS | Agent实时通信通道 |

---

## 详细API规范

### 1. Agent注册

```bash
POST /api/v2/agents/register
Content-Type: application/json

{
  "agent_id": "recruiter_agent_001",
  "agent_type": "recruiter",
  "owner_id": "enterprise_001",
  "owner_type": "enterprise",
  "capabilities": [
    "job_matching",
    "candidate_screening",
    "interview_scheduling",
    "offer_negotiation"
  ],
  "understood_taxonomies": ["talentos_core_v1"],
  "communication_protocols": ["ws", "http"]
}
```

响应：
```json
{
  "success": true,
  "certificate": {
    "certificate_id": "CERT-abc123def456",
    "agent_id": "recruiter_agent_001",
    "issued_at": "2026-04-25T00:14:00Z",
    "trust_score": 0.5,
    "verified_claims": {
      "registered_at": "2026-04-25T00:14:00Z"
    }
  }
}
```

### 2. 代理授权

```bash
POST /api/v2/agents/recruiter_agent_001/authorize
Content-Type: application/json

{
  "principal_id": "candidate_001",
  "principal_type": "individual",
  "agent_id": "recruiter_agent_001",
  "agent_type": "recruiter",
  "agent_capabilities": ["job_matching", "interview_scheduling"],
  "authorized_actions": [
    "search_jobs",
    "apply_to_jobs",
    "accept_interview_invitations"
  ],
  "denied_actions": ["accept_offers", "sign_contracts"],
  "constraints": {
    "salary_min": 500000,
    "salary_max": 800000,
    "denied_companies": ["competitor_corp"],
    "required_wlb_score": 0.7
  },
  "valid_from": "2026-04-25T00:00:00Z",
  "valid_until": "2026-12-31T23:59:59Z",
  "revocable": true
}
```

### 3. 偏好模型

```bash
POST /api/v2/preferences/model
Content-Type: application/json

{
  "model_id": "pref_candidate_001_v1",
  "owner_id": "candidate_001",
  "owner_type": "individual",
  "priorities": [
    {"dimension": "WLB", "weight": 0.9, "description": "工作生活平衡最重要"},
    {"dimension": "salary", "weight": 0.7, "description": "薪资要达到预期"},
    {"dimension": "growth", "weight": 0.6, "description": "成长空间"},
    {"dimension": "location", "weight": 0.3, "description": "地点可妥协"}
  ],
  "flexibilities": {
    "salary": {"can_flex_to": 0.8, "requires_approval_below": 0.6},
    "WLB": {"can_flex_to": 0.3, "requires_approval_below": 0.2, "never_below": 0.1}
  },
  "dealbreakers": [
    {"type": "company", "value": "competitor_corp", "strictness": 1.0},
    {"type": "location", "value": "三线城市", "strictness": 0.9}
  ],
  "counter_offer_authority": 0.6,
  "auto_accept_threshold": 0.85
}
```

### 4. 创建原子披露

```bash
POST /api/v2/disclosure/atoms
Content-Type: application/json

{
  "atom_id": "atom_skill_match_001",
  "content_type": "skill_match",
  "raw_value": {
    "python": 0.95,
    "fastapi": 0.88,
    "machine_learning": 0.75
  },
  "disclosure_level": "matched_only",
  "proof_type": "none",
  "owner_id": "candidate_001"
}
```

### 5. 开始谈判

```bash
POST /api/v2/negotiations/start?job_id=job_001&candidate_agent_id=candidate_agent_001&recruiter_agent_id=recruiter_agent_001
```

响应：
```json
{
  "success": true,
  "negotiation": {
    "negotiation_id": "NEG-abc123def456",
    "job_id": "job_001",
    "candidate_agent_id": "candidate_agent_001",
    "recruiter_agent_id": "recruiter_agent_001",
    "status": "pending",
    "current_round": 0,
    "requires_human_approval": false
  }
}
```

### 6. 创建提案

```bash
POST /api/v2/negotiations/NEG-abc123def456/propose
Content-Type: application/json

{
  "proposal_id": "PROP-xyz789",
  "negotiation_id": "NEG-abc123def456",
  "from_agent": "recruiter_agent_001",
  "to_agent": "candidate_agent_001",
  "content": {
    "salary": 650000,
    "bonus": 100000,
    "equity": "0.05%",
    "start_date": "2026-06-01",
    "title": "Senior Engineer"
  },
  "match_score": 0.82
}
```

### 7. 发送消息

```bash
POST /api/v2/messages/send
Content-Type: application/json

{
  "from_agent": "recruiter_agent_001",
  "to_agent": "candidate_agent_001",
  "intent": "interview_invitation",
  "content": {
    "job_id": "job_001",
    "interview_time": "2026-04-28T14:00:00Z",
    "interview_type": "technical",
    "duration_minutes": 60
  },
  "semantic_metadata": {
    "taxonomy_version": "talentos_core_v1",
    "concept_mappings": {
      "experience_years": "standard:5_years"
    }
  }
}
```

---

## WebSocket协议

### 连接

```javascript
const ws = new WebSocket("ws://localhost:8089/ws/agents");

ws.onopen = () => {
  // 认证
  ws.send(JSON.stringify({
    type: "auth",
    agent_id: "recruiter_agent_001"
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === "auth_success") {
    console.log("Connected!", msg.message);
  } else if (msg.type === "message") {
    console.log("New message from", msg.from_agent, msg.content);
  }
};
```

### 发送消息

```javascript
ws.send(JSON.stringify({
  type: "message",
  to_agent: "candidate_agent_001",
  content: {
    intent: "job_match_notification",
    job_id: "job_001",
    match_score": 0.92
  },
  timestamp: new Date().toISOString()
}));
```

---

## 数据模型

### Agent类型

```python
class AgentType(str, Enum):
    RECRUITER = "recruiter"      # 招聘Agent
    CANDIDATE = "candidate"       # 候选人Agent
    INTERVIEWER = "interviewer"  # 面试Agent
    ENTERPRISE = "enterprise"    # 企业Agent
```

### 披露级别

```python
class DisclosureLevel(str, Enum):
    PUBLIC = "public"            # 公开
    MATCHED_ONLY = "matched_only"  # 匹配后可见
    OFFER_ONLY = "offer_only"    # Offer阶段可见
    NEVER = "never"             # 永不披露
```

### 谈判状态

```python
class NegotiationStatus(str, Enum):
    PENDING = "pending"          # 待开始
    ACTIVE = "active"           # 进行中
    COUNTER_OFFER = "counter_offer"  # 还价中
    ACCEPTED = "accepted"       # 已接受
    REJECTED = "rejected"       # 已拒绝
    EXPIRED = "expired"         # 已过期
```

---

## 运行方式

### 启动API服务器

```bash
cd TalentAI_Pro
python -m api.server
```

或使用uvicorn：

```bash
cd TalentAI_Pro
uvicorn api.server:app --reload --port 8089
```

### 访问API文档

- Swagger UI: http://localhost:8089/docs
- ReDoc: http://localhost:8089/redoc

---

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 授权被拒绝 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

*文档版本：v1.0*
*日期：2026年4月25日*
*API版本：v2.0*
