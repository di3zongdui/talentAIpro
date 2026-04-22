# TalentAI Pro · 智觅

## API-First 技术架构与产品框架

> **产品代号**：TalentAI Pro / 智觅
> **核心战略**：API-First 特洛伊木马计划
> **定位**：AI招聘基础设施 + 双向交易撮合平台
> **版本**：v2.0
> **更新日期**：2026年4月22日

---

## 一、战略定位：API-First 特洛伊木马

### 1.1 双轮驱动战略

```
┌─────────────────────────────────────────────────────────────────┐
│                    API-First 特洛伊木马战略                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────────┐           ┌─────────────────┐              │
│   │   SaaS产品层    │  ──────▶ │   API平台层     │              │
│   │   (前端获客)    │   数据    │   (后端变现)    │              │
│   │                 │   回流    │                 │              │
│   └────────┬────────┘           └────────┬────────┘              │
│            │                             │                       │
│            │      ┌─────────────────┐      │                       │
│            └─────▶│   数据飞轮      │◀─────┘                       │
│                   │   Data Flywheel │                              │
│                   └─────────────────┘                              │
│                                                                   │
│   核心飞轮：产品用户 → 数据积累 → API能力 → 开发者生态 → 更多用户    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

获客路径（前端）：
├── 招聘者：注册 → 使用SaaS → 发现API能力 → 升级API套餐
├── 求职者：注册 → 使用候选人端 → 发现API能力 → 付费功能
└── 开发者：试用API → 集成到产品 → 商业合作 → 生态共建

变现路径（后端）：
├── SaaS订阅：月费/年费
├── API调用：按次计费
├── 企业定制：私有部署 + 定制开发
└── 数据服务：市场洞察报告
```

### 1.2 API-First 核心原则

```
API-First 设计原则：

1. 接口先行
   └── 所有功能先设计API，再实现UI
   └── API是产品能力的原子化呈现

2. 开发者体验（DX）优先
   ├── 文档完整：OpenAPI 3.0规范
   ├── SDK丰富：Python/JS/Go/Java多语言
   ├── 沙箱环境：免费测试额度
   └── 快速响应：<100ms P99延迟

3. 幂等性与可靠性
   ├── 所有写操作幂等
   ├── Webhook重试机制
   └── 完整的状态码定义

4. 版本管理
   ├── URL版本：/v1/, /v2/
   ├── 灰度发布：canary rollout
   └── 长期支持：LTS版本维护2年
```

---

## 二、系统架构：三层十二模块

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         接入层 (Gateway)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │
│  │ Web App│ │Mobile  │ │Plugin  │ │Feishu  │ │Open API│          │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         智能层 (AI Engine)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Matching Core 匹配引擎                     │   │
│  │  ├── Bidirectional Match 双向撮合                           │   │
│  │  ├── Surprise Discovery 超预期发现                          │   │
│  │  └── Commitment Assess 承诺评估                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ JD Engine   │ │Profile Eng.  │ │Interview Eng│               │
│  │ JD解析生成   │ │画像构建引擎  │ │面试引擎     │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ Reach Eng.  │ │Report Eng.  │ │Notify Eng.  │               │
│  │ 触达引擎    │ │报告引擎     │ │通知引擎     │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据层 (Data Layer)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  Candidate   │ │     Job      │ │  Behavior    │            │
│  │  Lake (PLM)  │ │  Lake (JLM)  │ │  Lake (BLM)  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  Vector DB   │ │  Graph DB    │ │    Cache     │            │
│  │  (Pinecone)  │ │  (Neo4j)     │ │   (Redis)    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 十二核心模块

```yaml
模块编号 | 模块名称 | 英文名 | 核心功能 | API暴露

M01    | JD引擎     | JDEngine    | JD解析/生成/优化    | ✅ /v1/jd/**
M02    | 画像引擎   | ProfileEng  | 人才/职位画像构建   | ✅ /v1/profile/**
M03    | 匹配引擎   | MatchEngine | 双向撮合/超预期发现  | ✅ /v1/match/**
M04    | 面试引擎   | InterviewEng| AI面试/评估/报告    | ✅ /v1/interview/**
M05    | 触达引擎   | ReachEngine | 全渠道个性化触达    | ✅ /v1/reach/**
M06    | 报告引擎   | ReportEng   | 面试报告/推荐报告   | ✅ /v1/report/**
M07    | 通知引擎   | NotifyEng   | 多渠道实时通知      | ✅ /v1/notify/**
M08    | 学习引擎   | LearnEngine | 模型持续优化/反馈   | 内部
M09    | 发现引擎   | DiscoveryEng| 多平台数据采集      | ✅ /v1/discovery/**
M10    | 飞书连接器 | FeishuConn  | 飞书深度集成        | ✅ /feishu/**
M11    | 微信连接器 | WechatConn  | 微信生态集成        | ✅ /wechat/**
M12    | 开放平台   | OpenPlatform| 开发者门户/API市场  | ✅ /api-market/**
```

---

## 三、Skills体系：三层十五Skill

### 3.1 Skills分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Skills 分层架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  第一层：客户端Skills（Client Skills）                            │
│  ────────────────────────────────────────────────────────────    │
│  定位：用户直接使用的AI能力，通过API调用后端                       │
│  特点：轻量、快速、可离线、用户友好                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  招聘者端（5个）         │  求职者端（5个）               │    │
│  ├─────────────────────────┼───────────────────────────────┤    │
│  │ jd-generator            │ candidate-profile-builder      │    │
│  │ resume-parser           │ job-matcher                    │    │
│  │ candidate-matcher       │ ai-interview-prep              │    │
│  │ interview-assistant     │ self-recommendation-writer     │    │
│  │ outreach-generator      │ application-tracker             │    │
│  └─────────────────────────┴───────────────────────────────┘    │
│                                                                   │
│  第二层：平台Skills（Platform Skills）                            │
│  ────────────────────────────────────────────────────────────    │
│  定位：后台能力增强，通过平台内部调用                              │
│  特点：重量级、强计算、需要数据湖                                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ discovery-radar    │ 多平台数据采集/超预期发现            │    │
│  │ vector-matcher     │ 向量检索/语义匹配                    │    │
│  │ graph-analyzer     │ 关系图谱/社交网络分析                │    │
│  │ sentiment-analyzer │ 情感分析/意向度评估                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  第三层：连接Skills（Connector Skills）                           │
│  ────────────────────────────────────────────────────────────    │
│  定位：API-First聚合层——颠覆为人类设计的SaaS平台                   │
│  特点：协议转换、事件监听、数据融合                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 协作平台连接器                                            │    │
│  │ feishu-jd-extractor  │ 飞书JD/简历提取                    │    │
│  │ feishu-interview-bot │ 飞书面试机器人                     │    │
│  │ github-connector     │ GitHub数据采集                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 招聘平台连接器（API-First聚合层）                            │    │
│  │ linkedin-connector   │ LinkedIn API                     │    │
│  │ indeed-connector    │ Indeed API                        │    │
│  │ liepin-connector    │ 猎聘开放平台API                    │    │
│  │ boss-connector      │ Boss直聘（非官方API）                │    │
│  │ maimai-connector    │ 脉脉API                           │    │
│  │ zhilian-connector   │ 智联招聘API                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.6 连接器Skills详解：API-First聚合层

**战略定位：用API颠覆为人类设计的SaaS招聘平台**

```
┌─────────────────────────────────────────────────────────────────┐
│          TalentAI Pro API聚合层 (Platform Aggregation Layer)            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   LinkedIn      Indeed       猎聘        Boss直聘      脉脉      │
│       │            │           │            │           │        │
│       ▼            ▼           ▼            ▼           ▼        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          Platform Connectors (平台连接器)                      │    │
│  │   统一Schema转换 → 去重合并 → 数据质量评分 → 时效管理        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          Unified Resume Lake (统一简历湖)                       │    │
│  │   同一个人 → 多平台数据融合 → 完整360°人才画像                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          AI Resume Intelligence (AI简历智能层)               │    │
│  │   多模态解析 → 技能图谱 → 职业轨迹推断 → 意向预测           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          Platform-Native Output (平台原生输出)               │    │
│  │   LinkedIn投递 · Boss直聘投递 · 猎聘投递 → 统一追踪         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Skill 20: linkedin-connector（领英连接器）
```yaml
功能: LinkedIn API聚合 + 高端人才数据采集

API能力:
  - OAuth 2.0 用户授权
  - 个人资料/工作经历/教育经历读取
  - 技能认可/推荐读取
  - 人脉关系图谱
  - 文章/动态内容

数据采集:
  - 公开简历数据
  - 职业轨迹验证
  - 技能图谱
  - 内容影响力

API端点:
  POST /v1/connector/linkedin/authorize
  POST /v1/connector/linkedin/sync
  GET  /v1/connector/linkedin/profile/{id}
  POST /v1/connector/linkedin/apply
```

#### Skill 21: indeed-connector（Indeed连接器）
```yaml
功能: Indeed职位/简历API + 市场数据

API能力:
  - 职位搜索（Job Search API）
  - 简历搜索（Resume API，雇主）
  - 薪资估算

数据采集:
  - 公开职位数据
  - 薪资实况
  - 公司评价

API端点:
  GET  /v1/connector/indeed/jobs/search
  GET  /v1/connector/indeed/jobs/{id}
  POST /v1/connector/indeed/resumes/search
```

#### Skill 22: liepin-connector（猎聘连接器）
```yaml
功能: 猎聘开放平台 + 高端人才库

API能力:
  - 企业认证授权
  - 简历库搜索
  - 职位发布
  - 候选人沟通

数据采集:
  - 年薪30万+高端人才
  - 猎头顾问上传简历
  - 企业直接发布JD

API端点:
  POST /v1/connector/liepin/auth
  GET  /v1/connector/liepin/resumes/search
  POST /v1/connector/liepin/jobs/publish
```

#### Skill 23: boss-connector（Boss直聘连接器）
```yaml
功能: Boss直聘数据采集 + 模拟直聊

技术实现:
  - Playwright浏览器自动化
  - 反爬对抗策略
  - 消息队列频率控制

数据采集:
  - 实时职位数据
  - 候选人主动求职信息
  - 薪资实况
  - 公司氛围评价

风险控制:
  - IP轮换策略
  - 请求频率限制
  - 合规使用协议

API端点:
  POST /v1/connector/boss/login
  GET  /v1/connector/boss/jobs/search
  GET  /v1/connector/boss/candidates/{id}
  POST /v1/connector/boss/message/send
```

#### Skill 24: maimai-connector（脉脉连接器）
```yaml
功能: 脉脉职场数据 + 社交洞察

API能力:
  - 用户资料读取
  - 工作经历验证
  - 匿名八卦
  - 职场问答

数据采集:
  - 职场人脉图谱
  - 公司内部员工数
  - 员工匿名评价
  - 人才流动趋势

洞察输出:
  - 公司文化氛围评分
  - 管理层口碑
  - 员工稳定性
  - 竞对人才分布

API端点:
  POST /v1/connector/maimai/authorize
  GET  /v1/connector/maimai/profile/{id}
  GET  /v1/connector/maimai/company/{id}/insights
  GET  /v1/connector/maimai/talent-flow
```

#### Skill 25: zhilian-connector（智联招聘连接器）
```yaml
功能: 智联招聘API + 批量处理

API能力:
  - 简历库搜索
  - 职位批量发布
  - 候选人管理

数据采集:
  - 传统行业简历
  - 校园招聘数据
  - 蓝领工人数据

适用场景:
  - 传统行业招聘
  - 校园招聘
  - 批量处理

API端点:
  POST /v1/connector/zhilian/auth
  GET  /v1/connector/zhilian/resumes/search
  POST /v1/connector/zhilian/jobs/batch-publish
```

### 3.7 统一简历湖（Unified Resume Lake）

```yaml
核心设计理念：
  "同一个人在不同平台只是不同视角"

统一候选人Schema：
{
  "unified_id": "uuid-xxx",
  "source_ids": {
    "linkedin": "li_abc123",
    "liepin": "lp_456",
    "boss": "boss_789",
    "maimai": "mm_111"
  },
  "basic_info": {
    "names": ["张三", "Zhang San"],
    "verified_phones": ["138xxxx1234"],
    "verified_emails": ["zhangsan@xxx.com"],
    "current_title": "高级算法工程师",
    "current_company": "字节跳动",
    "confidence": 0.95
  },
  "skills": {
    "all": ["Python", "TensorFlow", "推荐系统", "分布式系统"],
    "by_source": {
      "linkedin": ["Python", "TensorFlow"],
      "liepin": ["推荐系统", "算法工程师"],
      "boss": ["字节跳动", "算法"]
    }
  },
  "experience": [...],
  "education": [...],
  "inferred": {
    "true_current_company": "字节跳动",
    "hidden_strengths": ["开源贡献", "顶会论文"],
    "intention_score": 0.75
  }
}

融合策略：
  1. 主键合并：电话/邮箱/身份证
  2. 相似度合并：姓名+公司+职位模糊匹配
  3. 时效性加权：最近更新优先
  4. 完整性补全：多源互补
  5. 冲突解决：多源验证，取置信度最高
```

### 3.2 招聘者端Skills（Client Layer）

#### Skill 1: jd-generator（JD生成器）
```yaml
输入:
  - 自然语言: "招一个懂大模型的HR"
  - 语音: 录音文件
  - 文档: PDF/Word
  - 竞品JD: URL或文本

输出:
  - job_id: string
  - structured_jd: object
  - market_insights: object
  - candidate_expectations: object

API端点:
  POST /v1/jd/generate
  POST /v1/jd/parse
  GET  /v1/jd/{id}

调用链: M01(JDEngine) → M02(ProfileEng) → 数据湖
```

#### Skill 2: resume-parser（简历解析器）
```yaml
输入:
  - PDF/Word/图片简历
  - 文本粘贴
  - LinkedIn URL

输出:
  - candidate_id: string
  - structured_profile: object
  - enrichment_data: object
  - confidence_score: float

API端点:
  POST /v1/resume/parse
  POST /v1/resume/upload
  GET  /v1/candidate/{id}

调用链: M02(ProfileEng) → M09(DiscoveryEng) → M02(ProfileEng)
```

#### Skill 3: candidate-matcher（候选人匹配器）
```yaml
输入:
  - job_id: string
  - match_options: {top_k, diversity, strictness}

输出:
  - matches: array<MatchResult>
  - overall_insights: object
  - next_action: string

MatchResult:
  - candidate_id: string
  - match_score: float
  - recruiter_score: float
  - candidate_score: float
  - surprise_insights: object
  - commitment_willingness: float

API端点:
  POST /v1/match/jd-to-candidates
  POST /v1/match/batch
  GET  /v1/match/{match_id}

调用链: M03(MatchEngine) → M09(DiscoveryEng) → M03(MatchEngine)
```

#### Skill 4: interview-assistant（面试助手）
```yaml
输入:
  - candidate_id: string
  - job_id: string
  - interview_type: "ai_screening" | "technical" | "behavioral"
  - duration: 15 | 30 | 45 | 60

输出:
  - interview_id: string
  - questions: array<Question>
  - candidate_prep_materials: object

API端点:
  POST /v1/interview/start
  GET  /v1/interview/{id}
  GET  /v1/interview/{id}/report
  POST /v1/interview/{id}/feedback

调用链: M04(InterviewEng) → M03(MatchEngine) → M06(ReportEng)
```

#### Skill 5: outreach-generator（触达话术生成器）
```yaml
输入:
  - candidate_id: string
  - job_id: string
  - channel: "email" | "wechat" | "feishu" | "linkedin"
  - tone: "formal" | "friendly" | "casual"

输出:
  - content: string
  - subject: string (for email)
  - call_to_action: string

API端点:
  POST /v1/reach/generate
  POST /v1/reach/send
  GET  /v1/reach/templates

调用链: M05(ReachEngine) → M07(NotifyEng)
```

### 3.3 求职者端Skills（Client Layer）

#### Skill 6: candidate-profile-builder（候选人画像构建）
```yaml
输入:
  - resume: file | text
  - linkedin_token: string (optional)
  - github_token: string (optional)

输出:
  - candidate_id: string
  - full_profile: object
  - platform_data: object
  - career_state: enum
  - intention_score: float

API端点:
  POST /v1/candidate/profile/build
  POST /v1/candidate/profile/enrich
  GET  /v1/candidate/profile/{id}

调用链: M02(ProfileEng) → M09(DiscoveryEng) → M02(ProfileEng)
```

#### Skill 7: job-matcher（智能职位匹配）
```yaml
输入:
  - candidate_id: string
  - preferences: object
  - job_ids: array<string> (optional)

输出:
  - recommendations: array<JobMatchResult>
  - market_analysis: object

JobMatchResult:
  - job_id: string
  - match_score: float
  - candidate_score: float
  - recruiter_score: float
  - surprise_insights: object
  - apply_button: string

API端点:
  GET  /v1/candidate/jobs/recommend
  POST /v1/candidate/jobs/apply
  GET  /v1/candidate/applications

调用链: M03(MatchEngine) → M09(DiscoveryEng) → M03(MatchEngine)
```

#### Skill 8: ai-interview-prep（AI面试准备）
```yaml
输入:
  - candidate_id: string
  - job_id: string
  - mode: "practice" | "evaluation"

输出:
  - prep_report: object
  - suggested_questions: array
  - good_answer_examples: array
  - improvement_tips: array

API端点:
  POST /v1/candidate/interview/prep
  POST /v1/candidate/interview/simulate
  GET  /v1/candidate/interview/feedback/{id}

调用链: M04(InterviewEng) → M09(DiscoveryEng)
```

#### Skill 9: self-recommendation-writer（自我推荐信生成）
```yaml
输入:
  - candidate_id: string
  - job_id: string
  - version: "short" | "standard" | "detailed"
  - format: "markdown" | "pdf"

输出:
  - recommendation_letter: string
  - key_highlights: array
  - tailored_points: array

API端点:
  POST /v1/candidate/recommendation/generate
  GET  /v1/candidate/recommendation/{id}
  POST /v1/candidate/recommendation/download

调用链: M06(ReportEng) → M02(ProfileEng)
```

#### Skill 10: application-tracker（投递跟踪器）
```yaml
输入:
  - candidate_id: string

输出:
  - applications: array<ApplicationStatus>
  - timeline: array<Event>
  - next_actions: array<Suggestion>

ApplicationStatus:
  - job_id: string
  - company: string
  - status: enum
  - last_update: datetime
  - days_since_update: int

API端点:
  GET  /v1/candidate/tracker
  PUT  /v1/candidate/tracker/{id}
  POST /v1/candidate/tracker/sync

调用链: M07(NotifyEng) → M02(ProfileEng)
```

### 3.4 平台Skills（Platform Layer）

#### Skill 11: discovery-radar（发现雷达）
```yaml
功能: 多平台数据采集 + 超预期发现

采集平台:
  - GitHub: 代码/项目/贡献/技术栈
  - LinkedIn: 职业轨迹/人脉/文章
  - 知乎: 回答/文章/关注领域
  - 头条/公众号: 内容输出/影响力
  - 豆包/扣子: AI使用行为
  - Claude/ChatGPT: AI技能评估

发现能力:
  - 候选人亮点发现
  - 公司亮点发现
  - 团队亮点发现
  - 面试官风格推断

API端点:
  POST /v1/discovery/candidate
  POST /v1/discovery/company
  POST /v1/discovery/surprise
  GET  /v1/discovery/report/{type}/{id}

内部调用: M02, M03
```

#### Skill 12: vector-matcher（向量匹配器）
```yaml
功能: 语义向量检索 + 近似最近邻搜索

能力:
  - 百万级向量秒级召回
  - 多向量空间并行检索
  - 混合检索（向量+关键词）

场景:
  - JD到候选人向量匹配
  - 候选人到JD向量匹配
  - 技能图谱相似检索

API端点: (内部)
  POST /internal/vector/search
  POST /internal/vector/index
```

#### Skill 13: graph-analyzer（图谱分析器）
```yaml
功能: 社交关系图谱 + 网络分析

分析维度:
  - 共同联系人发现
  - 团队关系推断
  - 影响力中心识别
  - 信息传播路径

应用:
  - 内推可能性评估
  - 文化契合度分析
  - 团队适配度评估

API端点: (内部)
  POST /internal/graph/analyze
  GET  /internal/graph/path
```

#### Skill 14: sentiment-analyzer（情感分析器）
```yaml
功能: 文本情感 + 意向度推断

分析对象:
  - 简历文本情感倾向
  - 面试回答评估
  - 沟通消息意向
  - 社交内容风格

输出:
  - sentiment_score: float
  - key_emotions: array
  - confidence: float

API端点: (内部)
  POST /internal/sentiment/analyze
```

### 3.5 连接Skills（Connector Layer）

#### Skill 15-19: 平台连接器

```yaml
feishu-jd-extractor:
  功能: 从飞书消息/文档中提取JD
  触发词: /jd extract [引用|doc:xxx]
  API: POST /feishu/v1/jd/extract

feishu-interview-bot:
  功能: 飞书面试机器人
  触发词: /interview start @xxx
  API: POST /feishu/v1/interview/start

github-connector:
  功能: GitHub数据采集
  触发: 候选人授权
  API: POST /v1/discovery/github

linkedin-connector:
  功能: LinkedIn数据采集
  触发: 候选人授权
  API: POST /v1/discovery/linkedin

zhihu-connector:
  功能: 知乎数据采集
  触发: 候选人授权
  API: POST /v1/discovery/zhihu
```

---

## 四、API体系：五大类目

### 4.1 API总览

```
┌─────────────────────────────────────────────────────────────────┐
│                      TalentAI Pro API Platform                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 招聘者 API (Recruiter API)                    Base: /v1       │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /jd/generate          JD生成                           │ │
│  │ POST /jd/parse             JD解析                           │ │
│  │ GET  /jd/{id}              获取JD详情                       │ │
│  │ POST /jd/{id}/matches     获取匹配候选人                   │ │
│  │                                                     15+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 候选人 API (Candidate API)                  Base: /v1/candidate│ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /profile/build        构建画像                         │ │
│  │ GET  /jobs/recommend       推荐职位                        │ │
│  │ POST /interview/prep       面试准备                        │ │
│  │ POST /recommendation/gen   生成推荐信                      │ │
│  │ GET  /tracker              投递跟踪                        │ │
│  │                                                    20+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 匹配 API (Matching API)                     Base: /v1/match  │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /jd-to-candidates     JD→候选人匹配                   │ │
│  │ POST /candidate-to-jobs    候选人→JD匹配                   │ │
│  │ POST /batch               批量匹配                         │ │
│  │ GET  /{match_id}           获取匹配结果                    │ │
│  │                                                     10+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 面试 API (Interview API)                    Base: /v1/interview│
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /start                开始面试                        │ │
│  │ GET  /{id}/status          面试状态                       │ │
│  │ GET  /{id}/report          获取面试报告                   │ │
│  │ POST /{id}/feedback        提交反馈                       │ │
│  │                                                     12+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 发现 API (Discovery API)                    Base: /v1/discovery│ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /candidate            候选人数据采集                   │ │
│  │ POST /company              公司数据采集                    │ │
│  │ POST /surprise             超预期发现                      │ │
│  │ GET  /report/{type}/{id}   获取发现报告                   │ │
│  │                                                     8+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 平台 API (Platform API)                    Base: /v1/platform │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /auth/token           获取Token                       │ │
│  │ GET  /usage                使用量查询                      │ │
│  │ GET  /invoice              账单查询                        │ │
│  │ GET  /analytics            数据分析                        │ │
│  │                                                    10+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 飞书 API (Feishu API)                        Base: /feishu   │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ POST /connect              连接飞书                        │ │
│  │ POST /jd/sync              JD同步                         │ │
│  │ POST /candidate/sync       候选人同步                     │ │
│  │ POST /interview/schedule   面试安排                       │ │
│  │ POST /notify               发送通知                       │ │
│  │                                                    15+ API │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  总计: 90+ API endpoints                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 API认证与安全

```yaml
认证方式:
  1. API Key (推荐用于服务器到服务器)
     Header: X-API-Key: your-api-key

  2. OAuth 2.0 (推荐用于用户授权)
     Flow: Authorization Code
     Scope: read / write / admin

  3. JWT Token (用于Web/Mobile)
     Header: Authorization: Bearer <jwt-token>
     Expiry: 1小时 (access) / 7天 (refresh)

安全措施:
  - Rate Limiting: 100-10000 req/min (根据套餐)
  - IP Whitelist: 企业版可用
  - Webhook签名: HMAC-SHA256验证
  - 数据加密: TLS 1.3
```

### 4.3 API定价模型

```yaml
免费层 (Free):
  - 100 API calls/月
  - 1 workspace
  - 社区支持

入门层 (Starter): ¥299/月
  - 10,000 API calls/月
  - 5 workspaces
  - 邮件支持
  - 基本分析

专业层 (Professional): ¥999/月
  - 100,000 API calls/月
  - 无限 workspaces
  - 优先支持
  - 高级分析
  - Webhook支持

企业层 (Enterprise): ¥2999/月起
  - 无限 API calls
  - 私有部署选项
  - 专属CSM
  - SLA保障
  - 定制开发

按量付费:
  - 超出配额: ¥0.01/次
  - 额外workspace: ¥99/月/个
```

---

## 五、数据模型：核心实体

### 5.1 核心实体关系

```
┌─────────────────────────────────────────────────────────────────┐
│                    核心实体关系图                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│    ┌─────────┐         ┌─────────┐         ┌─────────┐        │
│    │ Company │         │   Job    │         │Candidate │        │
│    └────┬────┘         └────┬────┘         └────┬────┘        │
│         │                   │                   │               │
│         │ 1            M..M │ 1              1..M │              │
│         ▼                   ▼                   ▼               │
│    ┌─────────┐         ┌─────────┐         ┌─────────┐        │
│    │JD Profile│────────▶│  Match  │◀────────│Profile  │        │
│    └─────────┘         └────┬────┘         └─────────┘        │
│                             │                                 │
│                       ┌─────┴─────┐                           │
│                       │  Interview │                          │
│                       └─────┬─────┘                           │
│                             │                                 │
│                       ┌─────┴─────┐                           │
│                       │  Report   │                           │
│                       └───────────┘                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 核心数据结构

#### Candidate Profile
```json
{
  "candidate_id": "cand_abc123",
  "basic_info": {
    "name": "张三",
    "age": 32,
    "education": "硕士",
    "work_years": 8,
    "current_company": "字节跳动",
    "current_title": "高级算法工程师"
  },
  "skills": {
    "hard": ["Python", "TensorFlow", "PyTorch", "分布式系统"],
    "soft": ["团队协作", "沟通表达", "项目领导"]
  },
  "platform_data": {
    "github": {
      "username": "zhangsan",
      "repos": 25,
      "stars": 1500,
      "languages": ["Python", "Go"],
      "contributions": 1200
    },
    "linkedin": {
      "connections": 500,
      "articles": 12,
      "endorsements": ["Python", "ML"]
    }
  },
  "preferences": {
    "desired_salary": "150-200万",
    "preferred_locations": ["北京", "上海"],
    "preferred_company_types": ["互联网", "AI"],
    "remote_acceptable": true
  },
  "assessment": {
    "intention_score": 7.5,
    "commitment_willingness": 0.85,
    "culture_fit_scores": {}
  },
  "status": "active",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-04-20T15:30:00Z"
}
```

#### Job Profile
```json
{
  "job_id": "job_xyz789",
  "basic_info": {
    "title": "高级算法工程师",
    "company": "某AI公司",
    "location": "北京",
    "salary_range": "120-180万",
    "remote_policy": "hybrid"
  },
  "requirements": {
    "skills": ["Python", "TensorFlow", "推荐系统"],
    "work_years": "5年以上",
    "education": "本科及以上"
  },
  "preferences": {
    "bonus_for": ["开源贡献", "顶会论文", "管理经验"],
    "team_size": "10-20人",
    "tech_stack": "云原生, K8s"
  },
  "hiring_manager": {
    "name": "李经理",
    "style": "结果导向",
    "interview_notes": []
  },
  "status": "open",
  "created_at": "2026-04-10T09:00:00Z",
  "updated_at": "2026-04-20T14:00:00Z"
}
```

#### Match Result
```json
{
  "match_id": "match_456",
  "job_id": "job_xyz789",
  "candidate_id": "cand_abc123",
  "scores": {
    "overall": 0.89,
    "recruiter_satisfaction": 0.92,
    "candidate_satisfaction": 0.86,
    "recruiter_surprise": 0.25,
    "candidate_surprise": 0.18
  },
  "commitment": {
    "recruiter_willingness": 0.91,
    "candidate_willingness": 0.88,
    "can_proceed": true
  },
  "surprise_insights": {
    "for_recruiter": [
      "候选人GitHub项目被Vue3官方引用",
      "候选人曾在NeurIPS发表论文",
      "薪资期望低于预算15%"
    ],
    "for_candidate": [
      "公司C轮50亿估值",
      "CTO著有《AI实战》畅销书",
      "技术团队来自Google/Meta"
    ]
  },
  "recommendations": {
    "next_action": "发起AI初筛面试",
    "interview_focus": ["推荐系统实战", "大规模分布式经验"],
    "questions_to_ask": []
  },
  "created_at": "2026-04-22T10:00:00Z"
}
```

---

## 六、开发者生态

### 6.1 开发者门户

```
┌─────────────────────────────────────────────────────────────────┐
│                    developer.talentai.pro                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  文档中心 (Documentation)                                 │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  • API Reference (Swagger UI)                            │    │
│  │  • SDK下载 (Python/JS/Go/Java)                           │    │
│  │  • 快速开始 (5分钟上手)                                   │    │
│  │  • 教程 (按场景)                                          │    │
│  │  • 最佳实践                                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  API市场 (API Marketplace)                               │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  • 热门API推荐                                            │    │
│  │  • 行业解决方案                                            │    │
│  │  • 成功案例                                               │    │
│  │  • 定价计算器                                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  控制台 (Console)                                         │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  • API Key管理                                           │    │
│  │  • 使用量监控                                             │    │
│  │  • 日志查询                                               │    │
│  │  • 告警设置                                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  社区 (Community)                                        │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  • 开发者博客                                             │    │
│  │  • 技术论坛                                               │    │
│  │  • Slack/微信群                                          │    │
│  │  • 线下活动                                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 SDK支持

```yaml
官方SDK:
  Python:   talentai-python  (pip install talentai)
  JavaScript: talentai-js    (npm install talentai)
  Go:       talentai-go      (go get github.com/talentai/go)
  Java:     talentai-java    (Maven: groupId=ai.talentai)

社区SDK:
  Ruby:     talentai-ruby    (社区维护)
  PHP:      talentai-php     (社区维护)

Webhook支持:
  - 面试完成回调
  - 候选人响应回调
  - Offer状态变更回调
```

### 6.3 集成合作伙伴

```yaml
ATS集成:
  - 北森 (已认证)
  - Moka (已认证)
  - iTalent (开发中)

招聘平台:
  - Boss直聘 (插件形式)
  - 猎聘 (API对接)
  - 智联招聘 (API对接)

协作工具:
  - 飞书 (官方集成)
  - 钉钉 (官方集成)
  - 企业微信 (开发中)

日历/邮件:
  - Google Calendar (已支持)
  - Outlook (已支持)
  - 腾讯企业邮 (开发中)
```

---

## 七、特洛伊木马变现路径

### 7.1 用户转化路径

```
阶段1: SaaS获客 (Month 1-6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户路径:
  注册 → 免费试用(100次API) → 发现价值 → 升级付费套餐
  │
  ▼
转化指标:
  注册率: 40%
  试用→付费转化: 25%
  CAC: ¥500

阶段2: API深度使用 (Month 7-12)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户路径:
  付费SaaS → 开发者发现API → 试用API → 集成到产品 → 企业API套餐
  │
  ▼
转化指标:
  SaaS→API转化: 30%
  API ARPU: ¥5000/月
  CAC: ¥2000

阶段3: 生态锁定 (Year 2+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户路径:
  API重度使用 → 数据积累 → 产品深度集成 → 私有部署需求 → 战略合作
  │
  ▼
转化指标:
  API→企业定制: 15%
  企业ARPU: ¥10万/年
  LTV: ¥30万
```

### 7.2 收入结构演进

```yaml
Year 1:
  ├── SaaS订阅: 85%
  ├── API调用: 15%
  └── ARR目标: ¥500万

Year 2:
  ├── SaaS订阅: 60%
  ├── API调用: 35%
  └── ARR目标: ¥2000万

Year 3:
  ├── SaaS订阅: 40%
  ├── API调用: 50%
  ├── 企业定制: 10%
  └── ARR目标: ¥6000万

Year 4:
  ├── SaaS订阅: 30%
  ├── API调用: 50%
  ├── 企业定制: 15%
  ├── 数据服务: 5%
  └── ARR目标: ¥1.5亿
```

### 7.3 API-First 关键指标

```yaml
开发者获客指标:
  ├── 注册开发者数: 1000+
  ├── API调用量/月: 1000万+
  ├── 集成应用数: 50+
  └── 开发者NPS: 50+

变现指标:
  ├── ARPU: ¥5000/月(API用户)
  ├── Payback周期: 6个月
  ├── LTV/CAC: 5x
  └── 收入增长率: >100%/年

生态健康指标:
  ├── APImarket第三方收入占比: >20%
  ├── 合作伙伴续费率: >90%
  └── 平台引力指数: >0.5
```

---

## 九、核心运营决策

### 9.1 阈值设定机制：混合模式

```yaml
三层阈值体系：

第一层：系统默认值（冷启动）
├── 承诺触发阈值：75%
├── 超预期阈值：15%
├── 薪资匹配容忍：±20%
└── 经验匹配容忍：±2年
来源：行业基准 + 早期用户数据

第二层：双方自填（个性化）
招聘者设置：
├── 最低匹配分：60-90% 自定义
├── 必需要求：必须有 / 加分项 / 可妥协
├── 薪资范围：固定 / 可协商
└── 优先级权重：技能>薪资>经验

候选人设置：
├── 最低薪资：必须≥ / 期望≥
├── 地点偏好：必须 / 可选
├── 公司类型：强偏好 / 可妥协
└── 求职紧迫度：立即 / 1-3月 / 随便看看

第三层：动态学习（持续优化）
├── 招聘者行为：长期只选80%+ → 自动提高阈值
├── 候选人行为：多次拒绝A级匹配 → 提示降低期望
├── 反馈学习：面试通过/失败 → 调整权重
└── 市场校准：旺季/淡季 → 动态调整阈值
```

### 9.2 候选人侧付费模式：Freemium + HR补贴

```yaml
免费层（引流）：
├── 基础画像构建
├── 有限职位推荐（每天3个）
├── 基础投递跟踪
└── AI面试准备（1次/周）
目的：积累候选人池 → 数据飞轮

付费层（转化）：¥29/月 或 ¥199/年
├── 无限职位推荐
├── 无限AI面试模拟
├── 定制推荐信生成
├── 简历优化建议
└── 优先曝光给HR（标记"VIP候选人"）

HR补贴层（特殊场景）：
├── HR主动邀请：候选人免费获得深度服务
├── 精准内推：HR付费 → 候选人获得奖励
└── 紧急招聘：HR付费加速 → 候选人优先处理

收入结构：
├── 候选人付费：20% 收入（Year1-2）
├── HR内推补贴：30% 收入
└── 企业API套餐：50% 收入（Year3+）
```

### 9.3 观望池处理机制：触发式重评 + 主动提醒 + 降级曝光

```yaml
观望池定义：
├── 意向度 < 60% 的候选人
├── 超过30天无互动
└── 多次匹配未投递

处理机制：

第一层：触发式重评（主力机制）
├── 新JD发布 → 立即对池内相关候选人重跑匹配
├── 候选人更新画像（如GitHub新增项目）→ 立即对池内相关职位重跑
├── 招聘者更新JD → 立即对池内候选人重跑
└── 市场信号触发（薪资变化>10%、热门技能变化）→ 全池扫描

第二层：降级曝光（防骚扰）
├── 30天无互动 → 移入「备选池」（不主动推送，仅手动搜索可见）
├── 60天无互动 → 自动归档，邮件通知双方更新资料
└── 双方仍可在平台手动查看/激活

第三层：主动提醒（有节制）
├── 触发条件：有新的「超预期发现」
│   示例：候选人GitHub新增500 stars项目 / 公司完成新融资
├── 频率限制：每月最多2次，不超过1次/周
├── 内容要求：必须带「超预期」价值，不是机械的「您有新匹配」
└── 渠道：微信 > 短信 > 邮件（按触达率排序）
```

---

## 十、API-First 颠覆战略

### 9.1 为什么现有平台可以被颠覆

```
传统招聘平台的局限性：

LinkedIn:
├── 为人类阅读设计 → AI无法高效解析
├── 封闭API生态 → 数据孤岛
├── 会员订阅制 → 中小企业门槛高
└── 被动求职思维 → 主动寻访成本高

Boss直聘:
├── 反爬机制 → 竞品数据获取困难
├── 直聊模式 → 批量触达效率低
├── 单一市场 → 全球化能力弱
└── 用户体验优先 → API友好度低

猎聘:
├── 高端定位 → 覆盖人群有限
├── 猎头服务绑定 → 纯技术对接难
├── 数据格式不统一 → 整合成本高
└── 传统SaaS思维 → AI能力弱

脉脉:
├── 匿名八卦 → 数据可信度问题
├── 社交优先 → 简历数据不完整
├── 封闭生态 → 外部API极少
└── 用户习惯问题 → 工作场景使用率低
```

### 9.2 API-First 颠覆路径

```
TalentAI Pro 的颠覆策略：

第一层：数据聚合（不替代）
├── 通过API/模拟/API连接所有平台
├── 统一数据格式 → 打破数据孤岛
├── 多源数据融合 → 360°人才画像
└── 价值：比任何单一平台更了解候选人

第二层：AI赋能（增强现有）
├── 人类无法快速完成的事：
│   ├── 百万简历秒级匹配
│   ├── 跨平台同一候选人识别
│   ├── 候选人意向实时预测
│   └── 超预期亮点自动发现
└── 价值：让人类HR效率提升100倍

第三层：平台替代（最终目标）
├── 当我们的数据足够丰富
├── 当我们的AI足够精准
├── 当用户体验超越现有平台
└── 招聘者/求职者自然迁移
```

### 9.3 竞争壁垒构建

```
数据护城河（1-2年）：
├── 聚合5+平台数据
├── 建立统一简历湖
├── 跨平台同一人识别
└── 简历数据量>5000万

AI能力护城河（2-3年）：
├── 匹配准确率>90%
├── 超预期发现准确率>85%
├── 候选人意向预测准确率>80%
└── 面试评估与人工评估一致性>85%

网络效应护城河（3-5年）：
├── 招聘者越多 → 候选人数据越丰富
├── 候选人越多 → 职位匹配越精准
├── 开发者越多 → 集成场景越丰富
└── 数据飞轮 → 自我强化
```

### 9.4 平台连接优先级

```yaml
优先级排序（按战略价值和实现难度）：

P0 - 立即接入：
├── LinkedIn：高端人才，API完善
├── GitHub：技术能力验证，数据质量高
└── 猎聘：高端简历库，API开放

P1 - 快速跟进：
├── 脉脉：职场社交洞察，独有数据
├── 智联招聘：传统行业覆盖
└── Indeed：国际化职位数据

P2 - 中期规划：
├── Boss直聘：最大的直聊平台
├── 拉勾网：互联网垂直
└── 前程无忧：传统行业

P3 - 长期布局：
├── 各类行业垂直招聘平台
├── 海外各国本地招聘平台
└── 新兴招聘平台
```

---

## 八、Skills × API 矩阵

### 8.1 Skills与API映射

| Skill ID | Skill名称 | API端点 | 定价层级 | 备注 |
|:--------:|----------|---------|:--------:|------|
| S01 | jd-generator | POST /v1/jd/generate | Starter+ | |
| S02 | resume-parser | POST /v1/resume/parse | Starter+ | |
| S03 | candidate-matcher | POST /v1/match/jd-to-candidates | Professional | 批量另计 |
| S04 | interview-assistant | POST /v1/interview/start | Professional | 时长另计 |
| S05 | outreach-generator | POST /v1/reach/generate | Starter+ | |
| S06 | candidate-profile-builder | POST /v1/candidate/profile/build | Professional | |
| S07 | job-matcher | GET /v1/candidate/jobs/recommend | Professional | |
| S08 | ai-interview-prep | POST /v1/candidate/interview/prep | Starter+ | |
| S09 | self-recommendation-writer | POST /v1/candidate/recommendation/generate | Starter+ | |
| S10 | application-tracker | GET /v1/candidate/tracker | Free | |
| S11 | discovery-radar | POST /v1/discovery/surprise | Enterprise | |
| S12 | vector-matcher | (internal) | - | 内部服务 |
| S13 | graph-analyzer | (internal) | - | 内部服务 |
| S14 | sentiment-analyzer | (internal) | - | 内部服务 |
| S15-19 | 协作连接器 | POST /feishu/** | Professional | 飞书/钉钉 |
| S20 | linkedin-connector | POST /v1/connector/linkedin/** | Professional | |
| S21 | indeed-connector | GET /v1/connector/indeed/** | Professional | |
| S22 | liepin-connector | POST /v1/connector/liepin/** | Enterprise | |
| S23 | boss-connector | POST /v1/connector/boss/** | Enterprise | |
| S24 | maimai-connector | POST /v1/connector/maimai/** | Professional | |
| S25 | zhilian-connector | POST /v1/connector/zhilian/** | Professional | |

### 8.2 功能矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                    功能 × 套餐矩阵                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  功能                    │ Free │ Starter │ Pro │ Enterprise │   │
│  ────────────────────────────────────────────────────────────  │
│  JD生成                  │  10  │  500    │ 2K  │    ∞      │   │
│  简历解析                 │  10  │  500    │ 2K  │    ∞      │   │
│  候选人匹配               │  5   │  200    │ 1K  │    ∞      │   │
│  AI面试                   │  1   │  50     │ 200 │    ∞      │   │
│  触达话术                 │  10  │  500    │ 2K  │    ∞      │   │
│  多平台数据采集           │  ✗   │  ✗     │  ✓  │    ✓      │   │
│  超预期发现               │  ✗   │  ✗     │  ✓  │    ✓      │   │
│  飞书集成                 │  ✗   │  ✓     │  ✓  │    ✓      │   │
│  Webhook                  │  ✗   │  ✗     │  ✓  │    ✓      │   │
│  私有部署                 │  ✗   │  ✗     │  ✗  │    ✓      │   │
│  定制开发                 │  ✗   │  ✗     │  ✗  │    ✓      │   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

*文档版本：v2.0*
*日期：2026年4月22日*
*备注：API-First 架构设计为未来变现奠定基础*
