# TalentAI Pro - Phase 1 MVP

```
TalentAI_Pro/
├── models/                    # 数据模型
│   ├── __init__.py
│   ├── candidate.py           # 候选人模型
│   ├── job.py                # 职位模型
│   └── match.py              # 匹配结果模型
├── engine/                    # 核心引擎
│   ├── __init__.py
│   ├── matching_v1.py        # 匹配引擎 v1（基础版）
│   └── matching_v2.py        # 匹配引擎 v2（超预期版，待开发）
├── api/                      # API层
│   └── v1/
│       ├── __init__.py
│       ├── router.py         # API路由
│       ├── candidate.py      # 候选人API
│       ├── job.py            # 职位API
│       └── match.py          # 匹配API
├── skills/                   # Skills模块
│   ├── jd_parser/            # JD解析
│   ├── resume_parser/        # 简历解析
│   ├── discovery_radar/     # 超预期发现
│   └── smart_outreach/       # 智能触达
├── deal_tracker/             # 交易跟踪
├── db/                       # 数据库
│   └── database.py          # 数据库连接
└── tests/                   # 测试
    ├── test_matching.py
    └── test_api.py
```

## Phase 1 里程碑

| 模块 | 功能 | 状态 |
|------|------|------|
| models | 候选人/职位Schema定义 | ✅ |
| engine.matching_v1 | 基础匹配分计算 | ✅ |
| api.v1 | CRUD + 匹配接口 | ✅ |
| skills.jd_parser | JD文本解析 | ✅ |
| skills.resume_parser | 简历字段提取 | ✅ |

## 运行方式

```bash
# 安装依赖
pip install fastapi uvicorn pydantic

# 启动API服务
cd TalentAI_Pro
uvicorn api.v1.router:app --reload

# 运行测试
pytest tests/ -v
```
