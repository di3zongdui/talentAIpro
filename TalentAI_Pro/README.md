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
| | [实时顾问](frontend/consultant_realtime.html) | 实时多轮对话 |
| | [面试 Agent](frontend/interview_agent.html) | 智能面试评估 |
| | [Agent 生态](frontend/agent_ecosystem.html) | 多Agent协作 |
| **HR 演示** | [HR 端到端](frontend/hr_e2e_demo.html) | 完整招聘流程 |
| | [猎头-候选人匹配](frontend/recruiter_candidate_demo.html) | 智能匹配演示 |
| **管理后台** | [管理员后台](frontend/admin_dashboard.html) | 用户和权限管理 |
| | [开发者面板](frontend/developer_dashboard.html) | API密钥管理 |
| | [插件管理](frontend/plugin_manager.html) | 功能扩展 |

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
| `/api/interview/evaluate` | POST | 面试评估 |
| `/api/salary/negotiate` | POST | 薪资谈判 |
| `/api/semantic/match` | POST | 语义匹配 |

### WebSocket

| 端点 | 说明 |
|------|------|
| `/ws/agents` | Agent实时通信 |

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