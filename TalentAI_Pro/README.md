# TalentAI Pro - AI猎头系统

> 让AI成为每个猎头的超能力

## 🚀 快速开始

### 启动服务

```bash
# 方法1: 使用批处理脚本
run_server.bat

# 方法2: 手动启动
cd TalentAI_Pro
set PYTHONPATH=.
python api/server.py
```

服务启动后访问: **http://localhost:8089/**

---

## 📱 Home Page - 统一入口

打开 http://localhost:8089/ 进入系统主页，包含所有工具的导航入口：

| 分类 | 工具 | 说明 |
|------|------|------|
| **LLM & AI** | [LLM 测试面板](frontend/llm_test_dashboard.html) | 面试评估、薪资谈判、语义匹配 |
| | [LLM 配置](frontend/llm_config.html) | API Key和模型参数配置 |
| | [API 诊断](frontend/llm_diagnostic.html) | 端点测试和诊断 |
| **Agent 系统** | [顾问 Agent](frontend/consultant_agent.html) | AI招聘顾问 |
| | [面试 Agent](frontend/interview_agent.html) | 智能面试评估 |
| **HR 演示** | [候选人匹配](frontend/recruiter_candidate_demo.html) | 智能匹配演示 |

---

## 🛠️ 技术架构

```
TalentAI_Pro/
├── api/                          # API层
│   ├── server.py                 # FastAPI服务器 (端口8089)
│   ├── llm_routes.py             # LLM配置和控制API
│   ├── salary_routes.py          # 薪资谈判API
│   ├── semantic_routes.py        # 语义匹配API
│   ├── interview_routes.py       # 面试评估API
│   └── v2/                       # Agent API v2
├── llm/                          # LLM引擎
│   ├── __init__.py
│   ├── gateway.py                # LLM网关
│   ├── provider.py               # 模型提供商
│   └── registry.py               # 配置注册表
├── engine/                       # 核心引擎
│   ├── matching_v1.py            # 匹配引擎v1
│   └── matching_v2.py            # 匹配引擎v2
├── agents/                       # Agent系统
│   ├── consultant/               # 顾问Agent
│   └── interview/                # 面试Agent
└── frontend/                     # 前端页面
    ├── index.html                # 🏠 Home Page (入口)
    ├── llm_test_dashboard.html   # LLM测试面板
    └── ...
```

---

## 🔌 API端点

### 核心API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Home Page |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger API文档 |
| `/api/llm/configure` | POST | 配置LLM提供商 |
| `/api/llm/chat` | POST | LLM对话测试 |
| `/api/llm/negotiation-message` | POST | 薪资谈判消息生成（多轮记忆） |
| `/api/llm/negotiation-session/{id}` | GET | 获取谈判会话历史 |
| `/api/llm/negotiation-session/{id}` | DELETE | 清除谈判会话 |
| `/api/llm/negotiation-sessions` | GET | 列出所有谈判会话 |
| `/api/llm/negotiation-search` | GET | 搜索谈判会话 |
| `/api/workflow/multi-agent/negotiate` | POST | 多Agent谈判策略 |
| `/api/interview/intelligent-evaluation` | POST | 智能面试评估 |
| `/api/interview/evaluation/{id}` | GET | 获取评估结果 |
| `/api/interview/evaluations` | GET | 列出评估记录 |
| `/api/salary/negotiate` | POST | 薪资谈判 |
| `/api/semantic/match` | POST | 语义匹配 |

### WebSocket

| 端点 | 说明 |
|------|------|
| `/ws/agents` | Agent实时通信 |

---

## 🤝 薪资谈判 API（多轮记忆）

### POST `/api/llm/negotiation-message`

生成谈判消息，支持多轮对话记忆。

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `situation` | string | ✅ | 当前谈判情况描述 |
| `tone` | string | ✅ | 语气策略：`aggressive` / `moderate` / `conciliatory` |
| `candidate_info` | string | 首次 | 候选人背景信息 |
| `company_offer` | string | 首次 | 公司Offer内容 |
| `session_id` | string | 多轮 | 谈判会话ID（首次调用返回） |
| `candidate_reply` | string | 多轮 | 候选人最新回复 |

**首次调用示例：**

```json
POST /api/llm/negotiation-message
{
    "situation": "候选人面试通过，需要进行薪资谈判",
    "tone": "moderate",
    "candidate_info": "张三，5年经验，期望薪资25K-30K",
    "company_offer": "月薪22K，13薪，年终奖1-3个月"
}
```

**响应：**

```json
{
    "status": "success",
    "data": {
        "message": "张老师您好，非常认可您的能力。关于薪资，我们初步方案是22K*14薪，综合考虑您的经验我们还有空间，但需要您这边确认最终期望，我们再向上申请。",
        "session_id": "neg-a1b2c3d4e5f6",
        "round": 0
    }
}
```

**多轮调用示例：**

```json
POST /api/llm/negotiation-message
{
    "situation": "候选人觉得薪资偏低，需要进一步谈判",
    "tone": "moderate",
    "session_id": "neg-a1b2c3d4e5f6",
    "candidate_reply": "我觉得25K比较合理，能达到吗？"
}
```

**多轮响应示例：**

```json
{
    "status": "success",
    "data": {
        "message": "张老师，我们理解您的期望，经过综合评估，我们可以给到24K*14薪，这个方案已经是最大诚意了。",
        "session_id": "neg-a1b2c3d4e5f6",
        "round": 1,
        "context_summary": "谈判历史（共1轮）：\nHR: 您好，我们初步方案是22K*14薪...\n候选人: 我觉得25K比较合理..."
    }
}
```

### GET `/api/llm/negotiation-session/{session_id}`

获取谈判会话历史（从数据库读取，支持跨会话恢复）。

### DELETE `/api/llm/negotiation-session/{session_id}`

清除谈判会话（同时删除数据库记录）。

### GET `/api/llm/negotiation-sessions`

列出所有谈判会话（分页，参数：`?limit=20&offset=0&status=active`）。

### GET `/api/llm/negotiation-search?keyword=xxx`

搜索谈判会话（按候选人信息、offer、最终薪资等关键词）。

> 💾 **数据持久化**：谈判会话和消息自动存入 SQLite 数据库，服务器重启后可恢复历史记录，支持跨会话分析。

---

## 🎭 多Agent谈判 API

### POST `/api/workflow/multi-agent/negotiate`

同时调用 RecruiterAgent 和 CandidateAgent，模拟双方博弈，生成最优谈判策略。

**请求体：**

```json
{
    "job_id": "job-123",
    "candidate_id": "cand-456",
    "candidate_name": "张三",
    "candidate_expected_salary": "30K",
    "company_offer": "25K*14薪",
    "company_budget_max": "35K",
    "key_advantages": ["10年经验", "大厂背景", "全栈能力"],
    "red_lines": ["最低22K", "必须14薪以上"]
}
```

**响应：**

```json
{
    "success": true,
    "session_id": "multi-neg-a1b2c3d4e5f6",
    "recruiter_strategy": {
        "strategy": "moderate",
        "recommended_counter": "28K*14薪",
        "让步空间": ["可以适当提高薪资", "可以增加股票期权"],
        "候选人价值评估": "高价值候选人，建议重点争取"
    },
    "candidate_strategy": {
        "bottom_line": "26K",
        "flexible_points": ["可以接受股票期权替代部分现金"],
        "hard_points": ["不能低于26K", "必须14薪以上"]
    },
    "recommended_offer": "27K*14薪",
    "win_probability": 0.85
}
```

---

## 📊 智能面试评估 API

### POST `/api/interview/intelligent-evaluation`

基于简历+职位+问答，LLM生成个性化评估报告。

**请求体：**

```json
{
    "candidate_name": "李四",
    "candidate_resume": "5年Java开发经验，曾在BAT工作...",
    "job_title": "高级后端工程师",
    "job_requirements": ["Java", "Spring", "微服务", "MySQL"],
    "job_description": "负责核心系统架构设计...",
    "questions": [
        "请介绍一下你最擅长的技术栈",
        "如何设计一个高可用系统"
    ],
    "answers": [
        "我擅长Java生态，包括Spring Boot...",
        "高可用需要考虑..."
    ]
}
```

**响应：**

```json
{
    "success": true,
    "session_id": "interview-a1b2c3d4e5f6",
    "overall_score": 85,
    "overall_level": "good",
    "dimensions": [
        {
            "name": "技术能力",
            "score": 88,
            "level": "excellent",
            "evidence": ["对Spring生态理解深入", "能清晰解释微服务设计模式"],
            "suggestions": ["可加强分布式事务经验"]
        }
    ],
    "strengths": ["技术基础扎实", "沟通表达清晰"],
    "weaknesses": ["缺乏云原生经验"],
    "recommended_questions": ["如何处理分布式事务？"],
    "final_verdict": "建议录用"
}
```

### GET `/api/interview/evaluation/{session_id}`

获取评估结果（按 session_id）。

### GET `/api/interview/evaluations`

列出最近的评估记录（参数：`?limit=10`）。

---

## 📦 依赖安装

```bash
cd TalentAI_Pro
pip install -r requirements.txt
```

主要依赖：
- `fastapi` - Web框架
- `uvicorn` - ASGI服务器
- `pydantic` - 数据验证
- `httpx` - HTTP客户端
- `websockets` - WebSocket支持

---

## 🔧 开发指南

### 启动开发服务器

```bash
cd TalentAI_Pro
set PYTHONPATH=.
python api/server.py
```

### 运行测试

```bash
pytest tests/ -v
```

---

## 📄 License

MIT License - github.com/di3zongdui/talentAIpro