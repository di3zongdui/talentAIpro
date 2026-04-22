# TalentAI Pro · 智觅

## AI驱动的端到端智能招聘平台产品规划

> **产品代号**：TalentAI Pro / 智觅
> **定位**：AI时代的下一代招聘基础设施
> **核心战略**：从JD描述到面试报告，端到端自动化
> **分析日期**：2026年4月22日

---

## 一、产品名称与品牌重塑

### 1.1 新产品名称

| 名称 | 含义 | 定位 |
|------|------|------|
| **TalentAI Pro** | Talent + AI + Professional | 全球化品牌，专业AI招聘 |
| **智觅 (ZhiMi)** | 智慧寻觅 | 中国市场本地化品牌 |

### 1.2 名称选择理由

```
TalentAI Pro：
├── "Talent"：直接表达人才招聘核心业务
├── "AI"：强调AI驱动差异化
├── "Pro"：专业版定位，高端猎头市场
└── 便于全球化推广

智觅：
├── "智"：智慧、智能
├── "觅"：寻觅、发现
└── 朗朗上口，中文语境友好
```

### 1.3 品牌重塑理由

原"特洛伊木马JuiceBox"定位存在问题：
- "JuiceBox"在美国是成功品牌，但在中国知名度低
- "特洛伊木马"战略隐喻过于复杂
- 需要更直接的产品名称

---

## 二、市场机会与痛点

### 2.1 市场背景

```
市场规模：
├── 中国招聘市场规模：¥1000亿/年
├── AI招聘渗透率：<5%（处于爆发前夜）
├── LinkedIn退出中国留下的人才触达空白
└── 生成式AI技术成熟度已达到商用级别

时机窗口：
├── AI大模型能力爆发（GPT-4、Claude、通义、文心）
├── 企业降本增效压力下，AI替代人工招聘成为刚需
└── 候选人被动求职比例>70%，主动寻访需求强烈
```

### 2.2 核心痛点

```
HR/猎头痛点：
├── 简历筛选：1000份简历，人工筛选1周，漏选率>30%
├── 人才画像：缺乏数据支撑，凭感觉判断
├── 被动人才触达：LinkedIn退出后无好渠道
├── 面试效率：初筛面试消耗大量时间
└── JD编写：如何吸引目标人才

候选人痛点：
├── 简历石沉大海：投递后无反馈
├── 信息不对称：不知道HR真正想要什么
└── 面试准备：不知道面试官会问什么

企业痛点：
├── 招聘周期长：关键岗位空缺3-6个月
├── 招聘成本高：猎头佣金年薪20-30%
└── 人才流失：新员工6个月内离职率>20%
```

---

## 三、产品架构：三层AI引擎

### 3.1 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        接入层（多端入口）                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Web应用          浏览器插件         小程序          API开放平台       │
│  (HR工作台)       (Boss/猎聘)       (移动端)        (开发者集成)      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        智能层（AI引擎）                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ JD引擎   │  │ 画像引擎  │  │ 匹配引擎  │  │ 面试引擎  │         │
│  │ JD→结构化 │  │ 多维画像  │  │ 双向匹配  │  │ AI初面   │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ 触达引擎  │  │ 报告引擎  │  │ 通知引擎  │  │ 学习引擎  │         │
│  │ 全渠道   │  │ 面试报告  │  │ 微信/短信 │  │ 持续优化  │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层（人才知识库）                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     候选人数据湖                             │   │
│  │  ├── 基础简历数据（结构化）                                      │   │
│  │  ├── 多平台数据（GitHub/LinkedIn/知乎等）                         │   │
│  │  ├── 技能图谱（技术栈、专业领域）                                   │   │
│  │  ├── 职业轨迹（成长速度、稳定性）                                   │   │
│  │  └── 意向度评分（换工作可能性）                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     职位数据湖                               │   │
│  │  ├── JD文本库                                                │   │
│  │  ├── 技能需求图谱                                             │   │
│  │  └── 市场薪资基准                                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     行为数据湖                               │   │
│  │  ├── 匹配历史                                                │   │
│  │  ├── 面试反馈                                                │   │
│  │  └── 招聘结果                                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 核心AI引擎详解

#### JD引擎：从任意输入生成完整JD

```
输入形式：
├── 语音输入："我们需要一个懂AI的后端"
├── 文字描述："技术 leader，带过 10 人团队"
├── 文档上传：已有JD草案
└── 竞品参考：输入竞争职位描述

输出：
├── 完整JD结构（岗位职责、任职要求、薪资范围）
├── 技能标签提取（硬技能、软技能）
├── 面试问题模板
└── 候选人画像描述

技术实现：
├── 多模态理解（语音/图像/文本）
├── 意图识别 + 信息补全
└── 行业知识图谱（JD模板库）
```

#### 画像引擎：多维度人才画像

```
┌─────────────────────────────────────────────────────────────────┐
│                      候选人完整画像                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  基础层（简历数据）：                                               │
│  ├── 个人信息：姓名、年龄、学历、工作年限                            │
│  ├── 工作经历：公司、职位、时间、职责                               │
│  ├── 项目经验：项目描述、技术栈、成果                               │
│  └── 技能标签：技术栈、专业领域                                    │
│                                                                   │
│  扩展层（多平台数据）：                                             │
│  ├── GitHub：代码贡献、项目作品、技术栈、活动频率                    │
│  ├── LinkedIn：职业轨迹、人脉网络、文章活动                         │
│  ├── 知乎：专业问答、技术观点、行业认知                             │
│  ├── 头条/公众号：内容输出、专业影响力                              │
│  ├── 豆包/扣子：AI产品使用行为、技能偏好                            │
│  └── Claude/ChatGPT：AI使用场景、技能评估                          │
│                                                                   │
│  推断层（AI推断）：                                                 │
│  ├── 职业状态推断：在职/求职/观望                                  │
│  ├── 意向度评分：换工作可能性（1-10分）                             │
│  ├── 薪资期望：基于背景的合理薪资区间                               │
│  ├── 软技能评估：沟通能力、领导力、抗压能力                          │
│  └── 文化匹配度：与目标公司风格的匹配程度                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 人才画像数据结构

```json
{
  "candidate_id": "cand_xxx",
  "basic_info": {
    "name": "张三",
    "age": 32,
    "education": "硕士",
    "work_years": 8,
    "current_company": "字节跳动",
    "current_title": "高级算法工程师"
  },
  "multi_platform_profile": {
    "github": {
      "username": "zhangsan-github",
      "repos_count": 25,
      "total_stars": 1500,
      "top_languages": ["Python", "Go", "Rust"],
      "recent_activities": ["提交PR", "代码审查", "开源贡献"],
      "impact_score": 8.5
    },
    "linkedin": {
      "profile_url": "linkedin.com/in/zhangsan",
      "connections_count": 500,
      "articles_count": 12,
      "activity_frequency": "weekly",
      "endorsements": ["Python", "Machine Learning", "Leadership"]
    },
    "zhihu": {
      "followers": 3000,
      "answers_count": 45,
      "top_topics": ["AI", "算法", "职业发展"],
      "influence_score": 7.2
    },
    "developer_platforms": {
      "doubao": {"usage_frequency": "daily", "primary_use_cases": ["代码生成", "文案撰写"] },
      "kouzhi": {"created_bots_count": 5, "published": true },
      "claude": {"usage_frequency": "weekly", "use_cases": ["写作", "分析"] },
      "chatgpt": {"subscription_type": "Plus", "primary_use_cases": ["编程", "学习"] }
    }
  },
  "inferred_attributes": {
    "career_state": "passive_candidate",  // 被动候选人
    "intention_score": 6.5,               // 意向度 1-10
    "expected_salary_range": "150-200万",
    "soft_skills": {
      "communication": 8.5,
      "leadership": 7.0,
      "pressure_tolerance": 7.5
    },
    "cultural_fit": {
      "startup_score": 8.0,
      "big_company_score": 7.5
    }
  }
}
```

---

## 四、端到端AI面试系统

### 4.1 核心流程

```
招聘任务输入 → JD生成/解析 → 人才画像 → AI初筛面试 → 面试报告 → 推荐决策
     │              │            │            │            │            │
     ▼              ▼            ▼            ▼            ▼            ▼
  语音/文字      结构化JD     多维画像     AI提问       结构化报告    发送通知
  任意形式       精准匹配     多平台数据   自动评估     能力雷达图     多渠道
```

### 4.2 AI面试模块详细设计

#### 4.2.1 面试启动方式

```yaml
启动方式：
  1. 自动启动：
     条件：匹配度>80%，候选人确认参与
     流程：系统自动发送面试邀请 → 候选人选择时间 → AI面试官主持

  2. 手动启动：
     HR在后台点击"开始AI面试"
     可选择面试时长（15min/30min/45min）

  3. 批量启动：
     对多个候选人同时发起AI初筛
     系统自动安排时间窗口
```

#### 4.2.2 AI面试官能力

```
AI面试官核心能力：
├── 智能提问：根据候选人背景动态调整问题
├── 多轮对话：理解上下文，追问细节
├── 行为面试：STAR法则引导（Situation/Task/Action/Result）
├── 代码面试：实时Coding题目（可选）
├── 技术评估：基于GitHub项目提问
├── 情绪感知：识别候选人信心程度
└── 结构化评估：统一评判标准
```

#### 4.2.3 面试问题类型

```yaml
问题库：
  1. 技术问题：
     - 算法与数据结构
     - 系统设计
     - 项目细节追问
     - GitHub项目深入

  2. 行为问题：
     - 团队协作案例
     - 冲突解决经历
     - 失败与反思
     - 职业规划

  3. 文化匹配：
     - 工作方式偏好
     - 沟通风格
     - 价值观念

  4. 反向面试：
     - 候选人提问环节
     - 公司/团队介绍
```

#### 4.2.4 面试报告结构

```json
{
  "interview_id": "int_xxx",
  "candidate": "张三",
  "position": "高级算法工程师",
  "interview_time": "2026-04-22 10:00-10:30",
  "overall_score": 8.5,

  "detailed_assessment": {
    "technical_ability": {
      "score": 9.0,
      "strengths": ["算法功底扎实", "项目经验丰富", "技术视野广"],
      "concerns": ["大规模系统设计经验稍弱"],
      "key_findings": [
        "LeetCode 500+题，主要集中在算法和数据结构",
        "主导过推荐系统项目，用户转化率提升30%",
        "对分布式系统有实践但理论稍弱"
      ]
    },
    "communication": {
      "score": 8.5,
      "strengths": ["表达清晰", "逻辑性强"],
      "concerns": [],
      "key_findings": [
        "能够简洁明了地解释复杂技术问题",
        "主动分享项目经验和教训"
      ]
    },
    "cultural_fit": {
      "score": 8.0,
      "strengths": ["学习能力强", "抗压能力好"],
      "concerns": ["可能更偏好大公司文化"],
      "key_findings": [
        "希望有清晰的技术方向和文档",
        "不喜欢政治性的技术选型讨论"
      ]
    },
    "leadership_potential": {
      "score": 7.5,
      "strengths": ["有带团队意愿", "技术分享活跃"],
      "concerns": ["实际管理经验不足"],
      "key_findings": [
        "曾在开源社区组织技术分享",
        "希望未来转型技术管理"
      ]
    }
  },

  "recommendation": {
    "decision": "强烈推荐",
    "confidence": "高",
    "reason": "技术能力优秀，表达能力强，与团队文化高度契合",
    "next_steps": [
      "推荐直接进入技术终面",
      "建议安排系统设计面试"
    ]
  },

  "conversation_summary": {
    "duration": "28分钟",
    "questions_answered": 12,
    "code_exercises": 2,
    "candidate_questions": 3
  },

  "raw_transcript": "【完整面试对话记录】"
}
```

---

## 五、候选人发现与多平台数据整合

### 5.1 GitHub数据采集

```
采集维度：
├── 基础信息：用户名、头像、bio、位置
├── 仓库数据：repos数量、星标数、fork数
├── 编程语言：使用频率、技术栈偏好
├── 贡献活动：提交频率、代码审查、开源贡献
├── 项目作品：热门项目、个人项目、技术栈
└── 社交网络：followers/following、技术社区活跃度

评估指标：
├── 影响力量化：综合GitHub指标的Impact Score
├── 技术深度：热门项目数量、开源贡献质量
├── 技术广度：编程语言多样性
└── 活跃度：提交频率、最近活跃时间
```

### 5.2 LinkedIn数据采集

```
采集维度：
├── 职业轨迹：公司、职位、时间线
├── 教育背景：学校、专业、学历
├── 技能标签：行业技能、软技能认可
├── 人脉网络：连接数、共同联系人
├── 文章活动：发布内容、影响力
└── 线下活动：参与的行业活动、演讲

评估指标：
├── 职业发展速度：职级晋升频率
├── 人脉质量：连接数、共同联系人质量
├── 内容影响力：文章互动量、转发量
└── 行业认知度：关注者和被关注质量
```

### 5.3 知乎/内容平台数据采集

```
采集维度：
├── 回答内容：专业领域、回答质量
├── 文章输出：技术文章、观点输出
├── 关注者数量：专业影响力
├── 互动数据：点赞、评论、收藏
└── 专业话题：擅长领域的集中度

评估指标：
├── 专业深度：回答质量评分
├── 内容影响力：综合互动数据
└── 行业认可：同行的关注和认可
```

### 5.4 AI平台使用数据采集

```
采集平台：
├── 豆包（字节）：AI使用场景、频率、技能偏好
├── 扣子（字节）：Bot开发能力、发布的应用
├── Claude：使用场景、订阅等级
└── ChatGPT：使用场景、Plus/Pro订阅

评估指标：
├── AI熟练度：使用场景多样性和深度
├── AI工具创造能力：是否创建自己的AI工具
└── 学习能力：使用AI进行学习和工作的能力
```

---

## 六、多渠道通知系统

### 6.1 通知渠道矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                        通知渠道                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │  邮箱   │  │  微信   │  │  短信   │  │  APP   │           │
│  │         │  │         │  │         │  │  推送   │           │
│  │ 正式报告 │  │ 即时通知 │  │ 重要提醒 │  │ 随时查看 │           │
│  │ 附件为主 │  │ 链接为主 │  │ 简洁提醒 │  │ 完整功能 │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 通知场景

```yaml
通知场景：
  1. 面试完成通知：
     渠道：邮箱 + 微信 + APP
     内容：面试报告摘要 + 完整报告链接
     时效：面试完成后5分钟内

  2. 推荐候选人通知：
     渠道：微信 + 短信
     内容：候选人基本信息 + 匹配度 + 行动按钮
     时效：实时

  3. 候选人响应通知：
     渠道：微信 + APP
     内容：候选人确认/拒绝面试 + 候选人问题
     时效：实时

  4. 每日简报：
     渠道：邮箱
     内容：今日新增候选人 + 匹配动态 + 待处理事项
     时效：每日18:00

  5. 周报/月报：
     渠道：邮箱 + PDF附件
     内容：招聘漏斗分析 + 质量评估 + 优化建议
     时效：每周一/每月初
```

### 6.3 微信对话机器人

```
功能模块：
├── 即时查询：候选人信息、职位状态、面试进度
├── 报告推送：直接推送面试报告到微信
├── 快捷操作：确认面试、反馈结果、安排时间
└── 智能问答：回答HR常见问题

交互示例：
HR：帮我推荐3个算法工程师
Bot：【推荐1】张三 | 匹配度92% | 8年经验 | 字节背景
     【推荐2】李四 | 匹配度88% | 5年经验 | 阿里背景
     【推荐3】王五 | 匹配度85% | 6年经验 | 创业背景

HR：查看张三的详细报告
Bot：[发送报告链接] 点击查看完整报告
```

---

## 七、技术架构

### 7.1 技术栈

```
前端：
├── Web：React + TypeScript + TailwindCSS
├── 移动端：Flutter / React Native
└── 浏览器插件：Chrome Extension

后端：
├── 主服务：Python FastAPI + PostgreSQL + Redis
├── AI服务：Python + LangChain + 向量数据库
├── 实时服务：WebSocket + SSE
└── 任务队列：Celery + RabbitMQ

AI模型：
├── JD解析：GPT-4 / 通义千问 / 文心一言
├── 简历解析：多模态模型（文本+图像）
├── 智能匹配：自研匹配模型 + 向量检索
├── AI面试：GPT-4 + Speech-to-Text + Text-to-Speech
└── 报告生成：GPT-4 + 结构化模板

数据存储：
├── 结构化数据：PostgreSQL
├── 向量数据：Pinecone / Milvus
├── 文件存储：OSS / S3
├── 缓存：Redis
└── 日志：Elasticsearch
```

### 7.2 API设计

```yaml
核心API端点：

# JD管理
POST /api/v1/jd/generate      # 从任意输入生成JD
POST /api/v1/jd/parse         # 解析JD，提取结构化信息
GET  /api/v1/jd/{id}          # 获取JD详情

# 候选人管理
POST /api/v1/candidates/create      # 创建候选人
GET  /api/v1/candidates/{id}       # 获取候选人画像
POST /api/v1/candidates/search      # 多条件搜索
POST /api/v1/candidates/enrich      # 丰富候选人数据（多平台）

# 智能匹配
POST /api/v1/match/jd-to-candidates    # JD匹配候选人
POST /api/v1/match/candidate-to-jds    # 候选人匹配JD

# AI面试
POST /api/v1/interview/start           # 启动AI面试
GET  /api/v1/interview/{id}/status     # 获取面试状态
GET  /api/v1/interview/{id}/report     # 获取面试报告

# 通知管理
POST /api/v1/notify/send               # 发送通知
POST /api/v1/notify/wechat-bind        # 绑定微信
GET  /api/v1/notify/preferences        # 获取通知偏好

# Webhook
POST /api/v1/webhooks/interview-complete   # 面试完成回调
POST /api/v1/webhooks/candidate-response   # 候选人响应回调
```

---

## 八、与Cloud-Skills-Platform的整合

### 8.1 整合架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    TalentAI Pro 整合架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  原Cloud-Skills-Platform功能：                                    │
│  ├── resume-parser  →  整合为 JD引擎 + 简历解析                     │
│  ├── jd-analyzer    →  整合为 JD引擎核心                           │
│  ├── candidate-matcher → 整合为 匹配引擎核心                        │
│  ├── recommendation-writer → 整合为 报告引擎                       │
│  └── outreach-generator → 整合为 触达引擎                         │
│                                                                   │
│  新增功能：                                                        │
│  ├── GitHub数据采集                                                │
│  ├── LinkedIn数据采集                                              │
│  ├── 多平台数据整合                                                │
│  ├── AI面试引擎                                                   │
│  ├── 多渠道通知                                                   │
│  └── 微信对话机器人                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 数据流整合

```
数据飞轮 2.0：
                                                                   
  用户使用 → 数据采集 → 画像丰富 → 匹配优化 → 面试智能化 → 用户更多
      │                                                    │
      │         ↑                                          │
      └─────────┴──────────────────────────────────────────┘

新增数据源：
├── GitHub数据：技术能力验证
├── LinkedIn数据：职业轨迹验证
├── 内容平台数据：专业影响力评估
└── AI平台使用数据：AI时代新技能指标
```

---

## 九、产品路线图

### 9.1 MVP阶段（Month 1-3）

```
目标：验证核心价值主张

功能清单：
├── JD解析与生成（文字输入）
├── 基础简历解析
├── 人才画像（简历维度）
├── 简单匹配推荐
└── 基础面试报告生成

里程碑：
├── MVP上线
├── 10家种子客户
├── 简历解析准确率>90%
└── 匹配准确率>70%
```

### 9.2 PMF阶段（Month 4-6）

```
目标：产品市场匹配

功能清单：
├── 多平台数据采集（GitHub、LinkedIn）
├── 完整人才画像
├── AI初筛面试（15min）
├── 微信通知
├── 邮件报告
└── 浏览器插件

里程碑：
├── 50家付费客户
├── ¥50万ARR
├── 月流失率<5%
└── 客户NPS>40
```

### 9.3 规模化阶段（Month 7-12）

```
目标：快速增长

功能清单：
├── 端到端AI面试（45min）
├── 全渠道通知（微信/短信/APP）
├── 微信对话机器人
├── API开放平台
├── 多语言支持
└── 行业解决方案

里程碑：
├── 200家客户
├── ¥200万ARR
├── API收入占比>20%
└── 团队30人
```

### 9.4 生态建设阶段（Year 2）

```
目标：建立竞争壁垒

功能清单：
├── 猎头行业垂直模型
├── 企业定制化训练
├── 候选人端产品
├── 全球化扩展
└── 开放平台生态

里程碑：
├── 1000家客户
├── ¥1500万ARR
├── API收入占比>40%
└── 成为细分领域第一
```

---

## 十、商业模式

### 10.1 收入模型

```
SaaS订阅收入：
├── Starter：¥999/月（1-3个HR用户）
│   └── 包含：JD生成、简历解析、基础匹配、50次AI面试
├── Professional：¥2999/月（4-10个HR用户）
│   └── 包含：全功能、多平台数据、无限制AI面试、优先支持
├── Enterprise：¥9999/月（10+用户）
│   └── 包含：私有部署、定制开发、SLA保障、专属CSM
└── API套餐：按调用量计费

猎头版：
└── ¥1999/月/人
    └── 包含：候选人库管理、客户协作、AI面试、推荐报告
```

### 10.2 单位经济模型

```
客户获取成本（CAC）：
├── 内容营销+PLG：¥5000/客户
├── 销售驱动：¥20000/客户
└── 综合CAC：¥10000/客户

客户生命周期价值（LTV）：
├── 平均客单价：¥24000/年
├── 毛利率：80%
├── NRR：130%
├── 平均客户寿命：3年
└── LTV：¥24000 × 80% × 4 = ¥76,800

LTV/CAC = 7.68 ✅ （健康）
回本周期：10个月 ✅ （优秀）
```

---

## 十一、竞争优势

### 11.1 竞争壁垒

```
第一层：数据护城河（1-2年）
├── 1000万+简历数据
├── 100万+多平台人才数据
├── 10万+面试记录
└── 数据飞轮：越多客户→越好模型→越多客户

第二层：AI能力护城河（2-3年）
├── 招聘行业垂直模型
├── 多平台数据融合算法
├── AI面试评估模型
└── 持续优化：每次面试→算法改进

第三层：网络效应（3-5年）
├── HR用户网络
├── 候选人端产品
├── 企业客户网络
└── 开发者生态
```

### 11.2 与竞品差异化

```
vs. 传统ATS（北森、Moka）：
├── 他们：管理系统
├── 我们：智能引擎
└── 差异：AI Native

vs. Boss直聘/猎聘：
├── 他们：招聘平台
├── 我们：平台外能力
└── 差异：跨平台、深度分析

vs. 猎头公司：
├── 我们：AI替代低端工作
└── 差异：效率提升10倍

vs. JuiceBox.ai：
├── 我们：中国本土化
├── 支持：中国招聘平台
└── 差异：深度本土化、数据合规
```

---

## 十二、总结

### 12.1 核心价值

```
TalentAI Pro 智觅：
├── 输入：任意形式的招聘需求（语音/文字/文档）
├── 过程：AI自动解析→画像构建→智能匹配→AI初面→报告生成
├── 输出：面试报告+推荐决策+多渠道通知
└── 价值：招聘效率提升10倍，招聘成本降低50%
```

### 12.2 一句话总结

> **"TalentAI Pro 智觅：从一句招聘需求到一份面试报告，AI驱动招聘全流程自动化。"**

---

## 十三、双向交易撮合引擎（核心）

### 13.0 设计理念

```
传统招聘平台：单向流通（候选人 → 平台 → 企业）

TalentAI Pro 智觅：双向撮合（去中心化交易网络）

┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│                     ┌─────────────────┐                         │
│                     │  核心匹配引擎    │                         │
│                     │  Bidirectional  │                         │
│                     │  Matching Core  │                         │
│                     └────────┬────────┘                         │
│                              │                                   │
│            ┌─────────────────┼─────────────────┐              │
│            │                 │                 │              │
│            ▼                 ▼                 ▼              │
│     ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│     │  HR入口  │      │ 平台入口  │      │候选人入口│          │
│     │ Recruiter│      │  Admin  │      │Candidate │          │
│     └──────────┘      └──────────┘      └──────────┘          │
│                                                                   │
│  招聘者路径：JD输入 → AI画像 → 匹配候选人 → 发起面试 → 发送Offer     │
│  求职者路径：简历输入 → AI画像 → 匹配职位 → 发起面试 → 收到Offer     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 13.1 招聘者端流程（Forward Flow）

```
输入层：
├── 方式1：HR自然语言描述职位需求
│   "我需要一个懂大模型的算法工程师，最好有AIGC经验"
├── 方式2：上传JD文档/图片
├── 方式3：引用飞书群消息中的需求
├── 方式4：API接入（企业ATS系统）
└── 方式5：语音输入（移动端）

处理层：
├── JD解析引擎 → 结构化职位画像
├── 薪资基准分析 → 市场竞争力评估
├── 技能图谱构建 → 关键能力标签
└── 招聘难度预判 → 时间/成本预估

匹配层：
├── 向量检索 → Top-K候选人召回
├── 重排序模型 → 精排Top-20
├── 多维度评估 → 匹配分 + 匹配理由
└── 多样性保证 → 避免人才同质化

输出层：
├── 推荐候选人列表（带匹配理由）
├── 一键发起AI初筛
├── 批量外联（AI生成个性化邮件）
└── 实时进度追踪
```

### 13.2 求职者端流程（Reverse Flow）

```
输入层：
├── 方式1：上传简历（PDF/Word/图片）
├── 方式2：粘贴简历文本
├── 方式3：自然语言描述职业经历
│   "我在字节做了3年推荐算法，想看看外面的机会"
├── 方式4：语音输入（移动端）
├── 方式5：LinkedIn/GitHub账号授权自动导入
└── 方式6：API接入（候选人门户）

处理层：
├── 简历解析引擎 → 结构化人才画像
├── 多平台数据补充 → GitHub/LinkedIn/知乎
├── 职业状态推断 → 在职/求职/观望
├── 薪资期望分析 → 合理区间
└── 意向度评估 → 换工作紧迫程度

匹配层：
├── 向量检索 → Top-K职位召回
├── 双向匹配验证 → JD要求 vs 候选人期望
├── 市场竞争力分析 → 薪资/职级匹配
├── 公司文化契合度 → 组织风格匹配
└── 职业发展路径 → 成长空间评估

输出层：
├── 推荐职位列表（带匹配理由）
├── AI模拟面试准备
├── 自我推荐信生成（针对每个职位定制）
├── 一键投递（自动优化简历投递）
└── 投递跟踪（实时进度推送）
```

### 13.3 双向撮合核心逻辑

```python
# 核心匹配算法框架 v2.0 - 超预期撮合逻辑

class BidirectionalMatchingEngine:
    """
    双向撮合引擎 v2.0：
    - 核心目标：让双方都觉得"超出预期"，愿意做出承诺
    - 匹配分 = 基础匹配 + 超预期惊喜分
    - 承诺触发：双方分都 > 阈值 → 触发"展开沟通"行动
    """

    # 承诺触发阈值
    COMMITMENT_THRESHOLD = 0.75  # 超过75%预期即可触发承诺
    # 超预期阈值（比期望值高15%以上）
    EXCEED_THRESHOLD = 1.15

    def match(self, jd_profile, candidate_profile):
        # Step 1: 基础匹配（技能/经验/薪资）
        skill_score = self.skill_matching(jd_profile, candidate_profile)
        exp_score = self.experience_matching(jd_profile, candidate_profile)
        salary_score = self.salary_matching(jd_profile, candidate_profile)

        # Step 2: 招聘者视角 - 基础满意分
        recruiter_base_score = (
            skill_score * 0.4 +      # 技能匹配
            exp_score * 0.3 +        # 经验匹配
            self._check_preferences(jd_profile, candidate_profile) * 0.3
        )

        # Step 3: 候选人视角 - 基础满意分
        candidate_base_score = (
            skill_score * 0.25 +     # 能发挥技能
            exp_score * 0.2 +       # 经验被认可
            salary_score * 0.3 +    # 薪资满意
            self._check_company_preferences(jd_profile, candidate_profile) * 0.25
        )

        # Step 4: 超预期惊喜分计算（关键新增！）
        recruiter_surprise = self._calculate_surprise_for_recruiter(
            jd_profile, candidate_profile
        )
        candidate_surprise = self._calculate_surprise_for_candidate(
            jd_profile, candidate_profile
        )

        # Step 5: 综合分 = 基础分 × (1 + 惊喜加权)
        recruiter_final = recruiter_base_score * (1 + recruiter_surprise * 0.3)
        candidate_final = candidate_base_score * (1 + candidate_surprise * 0.3)

        # Step 6: 承诺意愿判断
        recruiter_willingness = self._assess_commitment_willingness(
            recruiter_base_score, recruiter_surprise
        )
        candidate_willingness = self._assess_commitment_willingness(
            candidate_base_score, candidate_surprise
        )

        # Step 7: 双向承诺触发
        can_proceed = (
            recruiter_willingness >= self.COMMITMENT_THRESHOLD and
            candidate_willingness >= self.COMMITMENT_THRESHOLD
        )

        # Step 8: 生成超预期亮点报告
        surprise_insights = self._generate_surprise_insights(
            jd_profile, candidate_profile, recruiter_surprise, candidate_surprise
        )

        return MatchResult(
            score=(recruiter_final + candidate_final) / 2,
            recruiter_score=recruiter_final,
            candidate_score=candidate_final,
            recruiter_willingness=recruiter_willingness,
            candidate_willingness=candidate_willingness,
            can_proceed=can_proceed,
            surprise_insights=surprise_insights,
            match_reasons=self._explain_both_sides(jd_profile, candidate_profile),
            next_actions=self._suggest_next_actions(
                can_proceed, recruiter_willingness, candidate_willingness
            )
        )

    def _calculate_surprise_for_recruiter(self, jd_profile, candidate_profile):
        """
        为招聘者计算"超预期惊喜分"
        发现候选人的亮点超出JD要求的部分
        """
        surprises = []

        #惊喜1: 候选人有额外热门项目
        if candidate_profile.github.hot_stars > 100:
            surprises.append(0.15)

        #惊喜2: 有开源贡献被主流项目接受
        if candidate_profile.github.pr_accepted_by_mainstream:
            surprises.append(0.2)

        #惊喜3: 有论文发表
        if candidate_profile.academic_papers:
            surprises.append(0.1)

        #惊喜4: 有管理经验（JD没写但候选人具备）
        if candidate_profile.management_experience and not jd_profile.requires_management:
            surprises.append(0.15)

        #惊喜5: 与未来同事有共同联系人
        if candidate_profile.mutual_connections_count > 3:
            surprises.append(0.1)

        #惊喜6: 薪资低于市场（成本优势）
        if candidate_profile.expected_salary < jd_profile.budget_salary * 0.9:
            surprises.append(0.1)

        return sum(surprises) / len(surprises) if surprises else 0

    def _calculate_surprise_for_candidate(self, jd_profile, candidate_profile):
        """
        为候选人生成"超预期惊喜分"
        发现公司/职位的亮点超出候选人期望的部分
        """
        surprises = []

        #惊喜1: 公司融资阶段好
        if jd_profile.company.funding_round in ['B', 'C', 'D']:
            surprises.append(0.15)

        #惊喜2: 薪资高于期望
        if jd_profile.salary_max > candidate_profile.expected_salary * self.EXCEED_THRESHOLD:
            surprises.append(0.2)

        #惊喜3: 团队技术密度高
        if jd_profile.company.tech_density == 'high':
            surprises.append(0.1)

        #惊喜4: 成长空间大
        if jd_profile.promotion_speed in ['fast', 'very_fast']:
            surprises.append(0.15)

        #惊喜5: 隐性福利好
        if jd_profile.company.benefits_count > 5:
            surprises.append(0.1)

        #惊喜6: 直属领导风格好
        if jd_profile.manager_style == 'servant_leader':
            surprises.append(0.15)

        #惊喜7: 公司技术栈前沿
        if jd_profile.tech_stack_modern_score > 0.8:
            surprises.append(0.1)

        return sum(surprises) / len(surprises) if surprises else 0

    def _assess_commitment_willingness(self, base_score, surprise_score):
        """
        评估承诺意愿：
        - 基础分 > 阈值（达到期望）
        - 超预期分 > 阈值（超出期望）
        → 愿意做出承诺（展开沟通/面试）
        """
        base_ok = base_score >= 0.6  # 达到基本期望
        exceed_ok = surprise_score >= 0.1  # 超出期望

        if base_ok and exceed_ok:
            return min(1.0, base_score + surprise_score * 0.5)
        elif base_ok:
            return base_score * 0.8  # 勉强愿意
        else:
            return base_score * 0.5  # 不愿意
```

### 13.4 交易状态机

```yaml
# 撮合交易状态机

交易状态定义：
  candidate_status:
    - NEW              # 新候选人入场
    - PROFILING        # 画像构建中
    - READY            # 画像完成，待推荐
    - MATCHED          # 已匹配到职位
    - INTERVIEWING     # 面试中
    - EVALUATING       # 评估中
    - OFFERED          # 已发Offer
    - HIRED            # 已入职
    - ARCHIVED         # 已归档

  job_status:
    - NEW              # 新职位发布
    - OPEN             # 开放招聘
    - SOURCING         # 寻访中
    - INTERVIEWING     # 面试中
    - OFFERING         # Offer沟通中
    - FILLED           # 已填坑
    - CLOSED           # 已关闭

状态转换规则：
  # 招聘者视角
  NEW_JD → OPEN:
    条件：JD画像完整度 > 80%
    动作：激活匹配引擎

  OPEN → SOURCING:
    条件：匹配到候选人
    动作：自动/手动发起联系

  SOURCING → INTERVIEWING:
    条件：候选人确认参与面试
    动作：安排AI/人工面试

  INTERVIEWING → OFFERING:
    条件：面试评估通过
    动作：发起Offer流程

  # 求职者视角
  NEW_RESUME → PROFILING:
    条件：简历上传成功
    动作：启动画像构建

  PROFILING → READY:
    条件：画像完整度 > 70%
    动作：开始职位推荐

  READY → MATCHED:
    条件：匹配到合适职位
    动作：发送推荐通知

  MATCHED → INTERVIEWING:
    条件：候选人确认面试
    动作：AI面试准备

  INTERVIEWING → OFFERED:
    条件：企业发送Offer
    动作：候选人确认
```

### 13.5 求职者端Skills

#### 13.5.1 candidate-profile-builder（候选人画像构建）

```yaml
功能：从任意输入构建完整候选人画像

输入：
  - 简历上传（PDF/Word/图片）
  - LinkedIn授权导入
  - GitHub授权导入
  - 自然语言描述职业经历
  - 语音输入

输出：
  - 完整人才画像（结构化）
  - 多平台数据补充
  - 职业状态评估
  - 意向度评分
  - 薪资期望区间

画像维度：
  基础层：教育背景、工作经历、技能证书
  扩展层：项目经验、成就贡献、培训经历
  推断层：软技能、领导力、潜力评估
  丰富层：GitHub/LInkedIn/知乎/AI平台数据
```

#### 13.5.2 job-matcher（智能职位匹配）

```yaml
功能：基于候选人画像，匹配最适合的职位

匹配策略：
  1. 技能匹配：核心技能 vs 职位要求
  2. 经验匹配：工作年限 vs 职位级别
  3. 薪资匹配：期望薪资 vs 职位预算
  4. 发展匹配：职业路径 vs 成长空间
  5. 文化匹配：个人风格 vs 公司文化

输出：
  - 推荐职位列表（Top 20）
  - 每个职位的匹配分
  - 匹配/不匹配原因
  - 改进建议（候选人视角）
  - 一键申请按钮
```

#### 13.5.3 ai-interview-prep（AI面试助手）

```yaml
功能：帮助候选人准备面试

能力：
  1. 职位分析：
     - 分析目标职位JD
     - 提取关键考察点
     - 预测高频问题

  2. AI模拟面试：
     - 基于简历和JD生成个性化问题
     - 实时语音/文字对话
     - 行为面试（STAR）引导

  3. 答案优化：
     - 提供优秀答案范例
     - 指出答案改进点
     - 模拟追问环节

  4. 面试复盘：
     - AI面试后生成评估报告
     - 针对弱项提供改进建议
```

#### 13.5.4 self-recommendation-writer（自我推荐信生成器）

```yaml
功能：为候选人生成定制化自我推荐信

针对每个职位定制：
  1. 职位分析：
     - 理解职位核心需求
     - 识别关键成功因素

  2. 亮点挖掘：
     - 从简历中挖掘匹配亮点
     - 量化成果（提升XX%，节省XX%）

  3. 定制撰写：
     - 开篇：吸引HR注意
     - 主体：2-3个核心亮点（STAR格式）
     - 结尾：行动号召

  4. 多版本输出：
     - 简洁版（150字，适合邮件）
     - 标准版（300字，适合附件）
     - 详细版（500字，适合补强）

输出格式：
  - Markdown
  - PDF
  - 直接复制文本
```

#### 13.5.5 discovery-radar（双向Discovery雷达）

```yaml
功能：在正式沟通前，为双方挖掘对方的"超预期亮点"

核心理念：
  "让招聘者和候选人都发现：对方比预期更好"
  → 产生积极惊喜 → 愿意做出承诺 → 展开沟通

为招聘者挖掘候选人亮点：
  1. GitHub深度发现：
     - 热门项目（>100 stars）的技术实现亮点
     - 开源贡献记录（被主流项目接受的PR）
     - 技术文章/博客（分享沉淀）
     - 代码之外的能力：社区影响力、技术布道

  2. LinkedIn深度发现：
     - 推荐信（同事/领导的真实评价）
     - 共同联系人（找到认识的人）
     - 线下活动演讲/分享
     - 获得的证书/荣誉
     - 升职轨迹（成长速度）

  3. 内容平台深度发现：
     - 知乎回答的技术深度和影响力
     - 公众号/博客的技术文章
     - 极客时间/知识星球等付费内容
     - 播客/视频分享
     - 行业会议的演讲记录

  4. 新闻/媒体发现：
     - 媒体报道中的提及
     - 创业经历/参与项目
     - 获得的奖项/荣誉
     - 行业影响力

为候选人挖掘公司/职位亮点：
  1. 公司深度发现：
     - 融资历史（投资机构背书）
     - 产品数据（用户增长/收入）
     - 技术博客（工程文化）
     - 开源项目（技术实力）
     - 专利/论文（创新投入）
     - 媒体报道（行业地位）

  2. 团队深度发现：
     - 未来同事的GitHub/Twitter
     - 团队技术博客
     - 团队成员构成（来自哪些大厂）
     - 管理层背景（行业资深程度）
     - 团队规模和技术密度

  3. 文化深度发现：
     - Glassdoor/脉脉员工评价（真实文化）
     - 996与否（work-life balance）
     - 晋升机制（成长空间）
     - 培训机制（学习机会）
     - 福利细节（隐性福利）

  4. 面试官深度发现：
     - LinkedIn背景（经历是否匹配）
     - 技术博客/分享（风格是否契合）
     - 共同经历（校友/同厂）
     - Twitter/微博（价值观）

超预期亮点生成：
  候选人为招聘者生成的惊喜报告：
    "🎯 超预期发现：
     - 候选人开源项目被Vue3官方仓库引用
     - 候选人曾在AI顶会NeurIPS发表论文
     - 候选人培养过10人+技术团队
     - 候选人与贵司CTO是清华校友"

  招聘者为候选人生成的惊喜报告：
    "🎯 超预期发现：
     - 公司刚完成C轮融资，估值50亿
     - 技术团队来自Google/ Meta/ 字节
     - 公司CTO著有《AI实战》畅销书
     - 公司人均产值200万（行业领先）
     - 团队使用前沿技术（GPT-4/Cadge/微服务）"

效果指标：
  - 惊喜发现数量：平均3-5个/候选人
  - 惊喜质量：70%超预期
  - 面试转化率提升：预期+30%
  - Offer接受率提升：预期+25%
```

#### 13.5.6 application-tracker（投递跟踪器）

```yaml
功能：自动跟踪候选人所有投递状态

跟踪范围：
  - 内部投递：通过平台的投递
  - 外部投递：同步自邮件/日历的投递
  - 候选人主动追踪：候选人在其他平台的投递

状态更新：
  - 自动更新：平台内状态变化
  - 手动同步：用户告知最新状态
  - 智能推断：基于邮件/日历推断状态

提醒场景：
  - 投递后X天无回音：自动提醒候选人跟进
  - 面试安排前1天：提醒候选人确认
  - Offer deadline临近：提醒候选人做决策
  - 候选人获得其他Offer：提醒对比机会

输出：
  - 投递状态看板
  - 时间线视图
  - 下一步行动建议
```

### 13.6 候选人端API设计

```yaml
# 候选人开放API

POST /api/v1/candidate/register        # 注册候选人
POST /api/v1/candidate/profile/build   # 构建画像
GET  /api/v1/candidate/profile/{id}    # 获取画像

POST /api/v1/candidate/resume/upload   # 上传简历
POST /api/v1/candidate/resume/parse    # 解析简历

GET  /api/v1/candidate/jobs/recommend  # 获取推荐职位
POST /api/v1/candidate/jobs/apply     # 申请职位
GET  /api/v1/candidate/applications    # 获取申请记录

POST /api/v1/candidate/interview/prep    # AI面试准备
POST /api/v1/candidate/interview/simulate # AI模拟面试
GET  /api/v1/candidate/interview/feedback # 获取面试反馈

POST /api/v1/candidate/recommendation/generate  # 生成推荐信
GET  /api/v1/candidate/recommendation/{id}       # 获取推荐信

POST /api/v1/candidate/discovery/company          # 为候选人生成公司惊喜报告
POST /api/v1/candidate/discovery/team             # 为候选人生成团队惊喜报告
POST /api/v1/candidate/discovery/interviewer      # 为候选人生成面试官惊喜报告

GET  /api/v1/recruiter/discovery/candidate       # 为招聘者生成候选人惊喜报告
POST /api/v1/recruiter/discovery/enrich          # 丰富候选人画像（深度发现）

GET  /api/v1/candidate/tracker          # 获取投递跟踪
PUT  /api/v1/candidate/tracker/{id}     # 更新投递状态

# Webhook
POST /api/v1/webhooks/application-status  # 投递状态变更回调
POST /api/v1/webhooks/interview-invite   # 面试邀请回调
POST /api/v1/webhooks/offer-received      # Offer收到回调
```

### 13.7 双向交付结果

```yaml
# 最终交付物定义

招聘者交付：
├── 候选人推荐列表（含匹配分）
├── AI面试报告（含评估）
├── 推荐决策建议
├── 候选人对比报告
└── 雇佣决策支持

候选人交付：
├── 匹配职位列表（含匹配分）
├── 自我推荐信（针对每个职位定制）
├── AI面试准备报告
├── 投递状态追踪
└── Offer对比分析（如有多家）

平台交付（双边）：
├── 交易撮合记录
├── 双向评价体系
├── 数据洞察报告
└── 市场基准分析
```

### 13.8 用户体验路径

```
路径一：HR快速发布职位（< 2分钟）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HR：输入"招一个懂大模型的HR"
        ↓
系统：理解需求 → 生成结构化JD → 确认
        ↓
系统：匹配20个候选人 → 发起批量外联
        ↓
HR：一键确认发送

路径二：候选人快速入职（< 30分钟）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
候选人：上传简历 / LinkedIn授权
        ↓
系统：构建画像 → 推荐10个职位 → 勾选感兴趣
        ↓
系统：为每个职位生成定制推荐信 → 一键投递
        ↓
系统：AI模拟面试 → 发现不足 → 提供改进建议
        ↓
候选人：准备充分 → 参加正式面试 → 收到Offer
```

---

## 十四、飞书深度集成模块（必选）

### 13.1 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    飞书生态深度集成                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  飞书群消息  │  │  飞书文档    │  │  飞书日程   │            │
│  │  实时监听   │  │  JD/简历    │  │  面试安排   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│          │                │                │                     │
│          ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              飞书数据采集引擎（Feishu Data Collector）     │   │
│  │  ├── 群聊消息解析（职位/候选人信息提取）                     │   │
│  │  ├── 文档内容抓取（JD/简历/通讯录）                        │   │
│  │  ├── 日程同步（面试安排/候选人时间）                        │   │
│  │  └── 联系人同步（员工/候选人）                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              飞书Skill层（Feishu Skills）                 │   │
│  │  ├── feishu-jd-extractor   → 飞书JD提取器                 │   │
│  │  ├── feishu-resume-parser  → 飞书简历解析器               │   │
│  │  ├── feishu-candidate-sync → 飞书候选人同步               │   │
│  │  ├── feishu-interview-bot  → 飞书面试机器人              │   │
│  │  └── feishu-reminder       → 飞书提醒助手                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              飞书API开放平台                              │   │
│  │  ├── /feishu/v1/jd/sync        → JD同步                  │   │
│  │  ├── /feishu/v1/candidates/sync → 候选人同步              │   │
│  │  ├── /feishu/v1/interview/schedule → 面试安排            │   │
│  │  └── /feishu/v1/notify         → 飞书通知                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2 飞书数据采集引擎

#### 13.2.1 飞书群消息监听

```
触发场景：
├── 群里发布职位需求（"急招AI算法工程师，简历发我"）
├── 群里推荐候选人（"@某某 帮我看看这个人选"）
├── 猎头顾问分享候选人信息
└── HR询问候选人进展

采集逻辑：
1. 关键词识别：
   - 职位相关：["招聘", "招人", "JD", "职位", "需求"]
   - 候选人相关：["简历", "人选", "候选人", "@"]
   - 动作相关：["发我", "帮我看看", "评估"]

2. 信息提取：
   - 发言人身份 → 顾问/HR身份识别
   - 消息时间 → 时效性判断
   - 附件内容 → 简历/JD文件
   - @提及 → 指定处理人

3. 自动处理：
   ├── 有简历附件 → 自动解析 → 创建候选人
   ├── 有JD描述 → 自动提取 → 创建职位
   └── 有候选人请求 → 自动匹配 → 推荐结果
```

#### 13.2.2 飞书文档自动同步

```
支持的飞书文档类型：
├── 招聘需求文档（多维表格）
├── 候选人简历文档
├── 面试评估表格
├── 候选人池管理表
└── 企业通讯录

同步机制：
├── 定时全量同步（每日凌晨）
├── 增量同步（文档修改时）
└── 手动触发同步（用户指令）

数据映射：
飞书多维表格 → 系统结构化数据
├── 第一列：姓名 → candidate.name
├── 第二列：联系方式 → candidate.phone/email
├── 第三列：当前公司 → candidate.current_company
├── 第四列：职位 → candidate.current_title
├── 第五列：技能标签 → candidate.skills
└── 第N列：自定义字段 → candidate.custom_fields
```

#### 13.2.3 飞书日历同步

```
日历事件类型：
├── 候选人面试（interview）
├──候选人推荐会议（recommendation）
├──候选人跟进（follow_up）
└── 系统提醒（reminder）

同步字段：
├── 事件标题：候选人姓名 + 面试类型
├── 时间：开始/结束时间
├── 参与者：HR、面试官、候选人（外链）
├── 地点：视频会议链接/办公室地址
├── 描述：面试官联系方式、注意事项
└── 附件：面试评估表链接

双向同步：
├── 飞书日历 → 系统：面试安排自动同步
├── 系统 → 飞书日历：候选人确认后自动创建日历事件
└── 候选人点击确认链接 → 自动同步到飞书
```

### 13.3 飞书Skill详细设计

#### 13.3.1 feishu-jd-extractor（飞书JD提取器）

```yaml
功能：从飞书任意位置（群消息/文档/日程）提取JD

输入方式：
  1. 引用飞书消息：
     "/jd extract [引用消息]"
     
  2. 指定飞书文档：
     "/jd extract doc:xxxxxxxxxx"
     
  3. 上传飞书文件：
     通过飞书机器人上传文件，自动识别处理

处理流程：
  1. 消息/文档内容识别
  2. 关键信息提取（职位/公司/薪资/技能）
  3. 结构化JD生成
  4. 存入JD库
  5. 自动发起匹配（可选）

输出：
  - JD ID
  - 结构化JD详情
  - 匹配候选人列表（Top 5）
  - 直接分享到群/私聊
```

#### 13.3.2 feishu-resume-parser（飞书简历解析器）

```yaml
功能：从飞书文档/消息/附件中解析简历

输入方式：
  1. 引用消息中的简历：
     "/resume parse [引用消息]"
     
  2. 上传飞书文件：
     发送到机器人，自动解析
     
  3. 飞书文档格式简历：
     "/resume parse doc:xxxxxxxxxx"

处理流程：
  1. 文件格式识别（PDF/Word/图片/在线文档）
  2. 多格式内容提取
  3. 简历结构化解析
  4. 人才画像生成
  5. 多平台数据补充（GitHub/LinkedIn）
  6. 存入候选人库

输出：
  - 候选人ID
  - 完整人才画像
  - 匹配职位列表（Top 5）
  - 分享到相关群/私聊
```

#### 13.3.3 feishu-candidate-sync（飞书候选人同步）

```yaml
功能：双向同步飞书联系人与候选人库

同步方向：
  1. 飞书 → 系统（被动人才库）：
     - 员工添加到飞书联系人
     - 自动创建候选人档案
     - 标记"前员工"状态
     
  2. 系统 → 飞书（候选人池）：
     - 候选人库成员
     - 自动同步到飞书联系人
     - 支持分组管理

同步内容：
  ├── 基本信息：姓名、电话、邮箱
  ├── 职业信息：公司、职位、部门
  ├── 技能标签：专业技能
  ├── 人才状态：在职/求职/观望
  └── 自定义字段：来源、意向度、备注
```

#### 13.3.4 feishu-interview-bot（飞书面试机器人）

```yaml
功能：在飞书群/私聊中发起和管理AI面试

核心能力：
  1. 发起面试：
     "/interview start @候选人 职位：算法工程师"
     
  2. 面试前提醒：
     - 候选人：面试时间、地点、注意事项
     - 面试官：候选人简历、关键问题提示
     
  3. 面试中辅助：
     - 实时转录（语音→文字）
     - 关键问题推荐
     - 计时提醒
     
  4. 面试后：
     - 自动生成面试报告
     - 分享到相关群/私聊
     - 下一步行动提醒

交互示例：
HR：/interview start 张三 高级算法工程师
Bot：✅ 面试已安排
     时间：2026-04-25 10:00-10:45
     候选人已收到邀请
     
Bot：📋 面试前提醒
     候选人：张三
     当前公司：字节跳动
     匹配度：92%
     
Bot：💡 建议提问
     1. 请介绍一下你在字节的项目
     2. 如何处理推荐系统的冷启动问题
     3. ...
```

#### 13.3.5 feishu-reminder（飞书提醒助手）

```yaml
功能：智能招聘提醒，不遗漏任何事项

提醒类型：
  1. 面试提醒：
     - 面试前24h/1h/15min
     - 候选人未确认提醒
     
  2. 跟进提醒：
     - 候选人发消息后未回复
     - 推荐后X天未反馈
     - 待发offer跟进
     
  3. 候选人动态提醒：
     - 候选人更换公司
     - 候选人发布新文章
     - 候选人GitHub新活跃
     
  4. 数据统计提醒：
     - 每日招聘数据简报
     - 每周推荐报告
     - 每月招聘漏斗分析

设置方式：
  /reminder set 面试提醒 1h @HR名称
  /reminder list  # 查看所有提醒
  /reminder delete 1  # 删除某条提醒
```

### 13.4 飞书API开放平台

```yaml
API端点设计：

# 飞书集成API
POST /feishu/v1/connect              # 连接飞书账号
GET  /feishu/v1/channels             # 获取已连接的群列表
POST /feishu/v1/subscribe            # 订阅群消息

# JD同步API
POST /feishu/v1/jd/sync              # 从飞书文档同步JD
GET  /feishu/v1/jd/{id}/matches      # 获取JD匹配结果

# 候选人API
POST /feishu/v1/candidates/sync      # 从飞书同步候选人
GET  /feishu/v1/candidates/{id}      # 获取候选人详情
POST /feishu/v1/candidates/{id}/enrich # 丰富候选人数据

# 面试API
POST /feishu/v1/interview/schedule   # 创建面试（同步到飞书日历）
GET  /feishu/v1/interview/{id}/report # 获取面试报告
POST /feishu/v1/interview/{id}/feedback # 提交面试反馈

# 通知API
POST /feishu/v1/notify/report        # 发送报告到飞书
POST /feishu/v1/notify/reminder      # 设置飞书提醒

# Webhook
POST /feishu/v1/webhooks/message     # 接收飞书消息
POST /feishu/v1/webhooks/doc_update # 接收文档更新
POST /feishu/v1/webhooks/calendar   # 接收日历事件
```

### 13.5 飞书机器人在CGL的落地场景

```
场景一：猎头顾问在飞书群发布需求
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HR（飞书群）：急招一个懂AI的HR负责人，年薪80-120万，有互联网背景
                                            ↓
                            Feishu JD Extractor 自动识别
                                            ↓
                            JD结构化 + 匹配候选人
                                            ↓
                            Bot回复：
                            ✅ JD已创建
                            🎯 推荐候选人（3位）：
                            1. 张三 | 匹配度94% | 前阿里HR
                            2. 李四 | 匹配度89% | 前字节HR
                            3. 王五 | 匹配度85% | 前美团HR
                            
场景二：顾问上传简历到飞书机器人
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

顾问（飞书私聊）：[发送PDF简历]
                    ↓
         Feishu Resume Parser 自动解析
                    ↓
         人才画像 + 多平台数据补充
                    ↓
         Bot回复：
         ✅ 简历已解析
         👤 张三 | 32岁 | 硕士
         🏢 前字节跳动 | 高级算法工程师
         🔧 技能：Python/TensorFlow/分布式系统
         📊 GitHub: 1.2k stars, 15 repos
         🔗 LinkedIn: 500+ connections
         
         🎯 匹配职位：
         1. 某AI公司算法负责人 | 匹配度92%
         2. 某独角兽AI总监 | 匹配度88%
         
场景三：AI面试完成自动推送报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI面试官：面试完成
                ↓
        面试报告生成
                ↓
        推送至飞书相关群
                ↓
群消息：
📋 面试报告：张三 - 高级算法工程师

技术能力：⭐⭐⭐⭐⭐ 9.0/10
沟通表达：⭐⭐⭐⭐⭐ 8.5/10
文化匹配：⭐⭐⭐⭐☆ 8.0/10

💡 建议：强烈推荐
📎 完整报告：[点击查看]

                ↓
HR直接点击查看/分享/安排下一轮面试
```

---

*文档版本：v1.1*
*日期：2026年4月22日*
*作者：George Guo*
