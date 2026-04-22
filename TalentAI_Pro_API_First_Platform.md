# TalentAI Pro · 智觅

## API First 招聘平台 - 完整设计文档

> **产品代号**：TalentAI Pro / 智觅
> **核心战略**：API-First 特洛伊木马计划
> **定位**：AI招聘基础设施 + 双向交易撮合平台
> **版本**：v1.0
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

| 模块编号 | 模块名称 | 英文名 | 核心功能 | API暴露 |
|:--------:|----------|---------|:--------:|------|
| M01 | JD引擎 | JDEngine | JD解析/生成/优化 | ✅ /v1/jd/** |
| M02 | 画像引擎 | ProfileEng | 人才/职位画像构建 | ✅ /v1/profile/** |
| M03 | 匹配引擎 | MatchEngine | 双向撮合/超预期发现 | ✅ /v1/match/** |
| M04 | 面试引擎 | InterviewEng | AI面试/评估/报告 | ✅ /v1/interview/** |
| M05 | 触达引擎 | ReachEngine | 全渠道个性化触达 | ✅ /v1/reach/** |
| M06 | 报告引擎 | ReportEng | 面试报告/推荐报告 | ✅ /v1/report/** |
| M07 | 通知引擎 | NotifyEng | 多渠道实时通知 | ✅ /v1/notify/** |
| M08 | 学习引擎 | LearnEngine | 模型持续优化/反馈 | 内部 |
| M09 | 发现引擎 | DiscoveryEng | 多平台数据采集 | ✅ /v1/discovery/** |
| M10 | 飞书连接器 | FeishuConn | 飞书深度集成 | ✅ /feishu/** |
| M11 | 微信连接器 | WechatConn | 微信生态集成 | ✅ /wechat/** |
| M12 | 开放平台 | OpenPlatform | 开发者门户/API市场 | ✅ /api-market/** |

---

## 三、Skills体系：三层二十五Skill

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
│  │ outreach-generator      │ application-tracker            │    │
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

---

## 四、核心匹配算法：双向撮合引擎 v2.0

### 4.1 设计理念

```
传统招聘平台：单向流通（候选人 → 平台 → 企业）

TalentAI Pro 智觅：双向撮合（去中心化交易网络）

核心目标：让双方都觉得"超出预期"，愿意做出承诺
匹配分 = 基础匹配 + 超预期惊喜分
承诺触发：双方分都 > 阈值 → 触发"展开沟通"行动
```

### 4.2 核心算法

```python
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

        return MatchResult(
            score=(recruiter_final + candidate_final) / 2,
            recruiter_score=recruiter_final,
            candidate_score=candidate_final,
            recruiter_willingness=recruiter_willingness,
            candidate_willingness=candidate_willingness,
            can_proceed=can_proceed,
            surprise_insights=self._generate_surprise_insights(...),
            next_actions=self._suggest_next_actions(...)
        )

    def _calculate_surprise_for_recruiter(self, jd_profile, candidate_profile):
        """为招聘者计算"超预期惊喜分""""
        surprises = []

        # 惊喜1: 候选人有额外热门项目
        if candidate_profile.github.hot_stars > 100:
            surprises.append(0.15)

        # 惊喜2: 有开源贡献被主流项目接受
        if candidate_profile.github.pr_accepted_by_mainstream:
            surprises.append(0.2)

        # 惊喜3: 有论文发表
        if candidate_profile.academic_papers:
            surprises.append(0.1)

        # 惊喜4: 与未来同事有共同联系人
        if candidate_profile.mutual_connections_count > 3:
            surprises.append(0.1)

        return sum(surprises) / len(surprises) if surprises else 0

    def _calculate_surprise_for_candidate(self, jd_profile, candidate_profile):
        """为候选人生成"超预期惊喜分" """
        surprises = []

        # 惊喜1: 公司融资阶段好
        if jd_profile.company.funding_round in ['B', 'C', 'D']:
            surprises.append(0.15)

        # 惊喜2: 薪资高于期望
        if jd_profile.salary_max > candidate_profile.expected_salary * self.EXCEED_THRESHOLD:
            surprises.append(0.2)

        # 惊喜3: 团队技术密度高
        if jd_profile.company.tech_density == 'high':
            surprises.append(0.1)

        return sum(surprises) / len(surprises) if surprises else 0
```

---

## 五、运营决策

### 5.1 阈值设定机制：混合模式

```yaml
三层阈值体系：

第一层：系统默认值（冷启动）
├── 承诺触发阈值：75%
├── 超预期阈值：15%
├── 薪资匹配容忍：±20%
└── 经验匹配容忍：±2年

第二层：双方自填（个性化）
├── 招聘者设置：最低匹配分60-90%自定义
└── 候选人设置：最低薪资、地点偏好、求职紧迫度

第三层：动态学习（持续优化）
├── 招聘者行为：长期只选80%+ → 自动提高阈值
└── 候选人行为：多次拒绝A级匹配 → 提示降低期望
```

### 5.2 候选人侧付费模式：Freemium + HR补贴

```yaml
免费层（引流）：
├── 基础画像构建
├── 有限职位推荐（每天3个）
└── AI面试准备（1次/周）

付费层（转化）：¥29/月 或 ¥199/年
├── 无限职位推荐
├── 无限AI面试模拟
├── 定制推荐信生成
└── 优先曝光给HR

HR补贴层（特殊场景）：
├── HR主动邀请：候选人免费获得深度服务
└── 精准内推：HR付费 → 候选人获得奖励
```

### 5.3 观望池处理机制

```yaml
观望池定义：
├── 意向度 < 60% 的候选人
├── 超过30天无互动
└── 多次匹配未投递

处理机制：

第一层：触发式重评（主力机制）
├── 新JD发布 → 立即对池内相关候选人重跑匹配
├── 候选人更新画像 → 立即对池内相关职位重跑
└── 市场信号触发 → 全池扫描

第二层：降级曝光（防骚扰）
├── 30天无互动 → 移入「备选池」
├── 60天无互动 → 自动归档，邮件通知双方更新
└── 双方仍可在平台手动查看/激活

第三层：主动提醒（有节制）
├── 触发条件：有新的「超预期发现」
├── 频率限制：每月最多2次，不超过1次/周
└── 渠道：微信 > 短信 > 邮件
```

---

## 六、API体系

### 6.1 API总览

```
TalentAI Pro API Platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

招聘者 API (Recruiter API)                    Base: /v1
─────────────────────────────────────────────────────────────
POST /jd/generate          JD生成
POST /jd/parse             JD解析
GET  /jd/{id}              获取JD详情
POST /jd/{id}/matches     获取匹配候选人               15+ API

候选人 API (Candidate API)                  Base: /v1/candidate
─────────────────────────────────────────────────────────────
POST /profile/build        构建画像
GET  /jobs/recommend       推荐职位
POST /interview/prep       面试准备
POST /recommendation/gen   生成推荐信                  20+ API

匹配 API (Matching API)                     Base: /v1/match
─────────────────────────────────────────────────────────────
POST /jd-to-candidates     JD→候选人匹配
POST /candidate-to-jobs    候选人→JD匹配
POST /batch               批量匹配                     10+ API

面试 API (Interview API)                    Base: /v1/interview
─────────────────────────────────────────────────────────────
POST /start                开始面试
GET  /{id}/status          面试状态
GET  /{id}/report          获取面试报告               12+ API

发现 API (Discovery API)                    Base: /v1/discovery
─────────────────────────────────────────────────────────────
POST /candidate            候选人数据采集
POST /company              公司数据采集
POST /surprise             超预期发现                   8+ API

飞书 API (Feishu API)                        Base: /feishu
─────────────────────────────────────────────────────────────
POST /connect              连接飞书
POST /jd/sync              JD同步
POST /candidate/sync       候选人同步
POST /interview/schedule   面试安排                   15+ API

总计: 90+ API endpoints
```

### 6.2 API认证与安全

```yaml
认证方式:
  1. API Key (服务器到服务器)
     Header: X-API-Key: your-api-key

  2. OAuth 2.0 (用户授权)
     Flow: Authorization Code

  3. JWT Token (Web/Mobile)
     Header: Authorization: Bearer <jwt-token>
     Expiry: 1小时 (access) / 7天 (refresh)

安全措施:
  - Rate Limiting: 100-10000 req/min
  - IP Whitelist: 企业版可用
  - Webhook签名: HMAC-SHA256验证
  - 数据加密: TLS 1.3
```

### 6.3 API定价模型

```yaml
免费层 (Free):
  - 100 API calls/月
  - 1 workspace

入门层 (Starter): ¥299/月
  - 10,000 API calls/月
  - 5 workspaces
  - 邮件支持

专业层 (Professional): ¥999/月
  - 100,000 API calls/月
  - 无限 workspaces
  - 优先支持
  - Webhook支持

企业层 (Enterprise): ¥2999/月起
  - 无限 API calls
  - 私有部署选项
  - SLA保障
```

---

## 七、平台连接器：API-First聚合层

### 7.1 战略定位

```
用API颠覆为人类设计的SaaS招聘平台

LinkedIn      Indeed       猎聘        Boss直聘      脉脉
    │            │           │            │           │
    ▼            ▼           ▼            ▼           ▼
┌─────────────────────────────────────────────────────────┐
│          Platform Connectors (平台连接器)                      │
│   统一Schema转换 → 去重合并 → 数据质量评分 → 时效管理        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          Unified Resume Lake (统一简历湖)                       │
│   同一个人 → 多平台数据融合 → 完整360°人才画像                │
└─────────────────────────────────────────────────────────┘
```

### 7.2 连接器优先级

```yaml
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
```

---

## 八、统一简历湖

### 8.1 核心设计理念

```
"同一个人在，不同平台只是不同视角"
```

### 8.2 统一候选人Schema

```json
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
  "inferred": {
    "true_current_company": "字节跳动",
    "hidden_strengths": ["开源贡献", "顶会论文"],
    "intention_score": 0.75
  }
}
```

### 8.3 融合策略

```yaml
融合策略：
  1. 主键合并：电话/邮箱/身份证
  2. 相似度合并：姓名+公司+职位模糊匹配
  3. 时效性加权：最近更新优先
  4. 完整性补全：多源互补
  5. 冲突解决：多源验证，取置信度最高
```

---

## 九、颠覆战略

### 9.1 为什么现有平台可以被颠覆

```
传统招聘平台的局限性：

LinkedIn:
├── 为人类阅读设计 → AI无法高效解析
├── 封闭API生态 → 数据孤岛
└── 会员订阅制 → 中小企业门槛高

Boss直聘:
├── 反爬机制 → 竞品数据获取困难
├── 直聊模式 → 批量触达效率低
└── 用户体验优先 → API友好度低

猎聘:
├── 高端定位 → 覆盖人群有限
├── 猎头服务绑定 → 纯技术对接难
└── 传统SaaS思维 → AI能力弱
```

### 9.2 API-First 颠覆路径

```
TalentAI Pro 的颠覆策略：

第一层：数据聚合（不替代）
├── 通过API/模拟/API连接所有平台
├── 统一数据格式 → 打破数据孤岛
└── 多源数据融合 → 360°人才画像

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
└── 招聘者/求职者自然迁移
```

---

## 十、特洛伊木马变现路径

### 10.1 用户转化路径

```
阶段1: SaaS获客 (Month 1-6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户路径:
  注册 → 免费试用(100次API) → 发现价值 → 升级付费套餐
转化指标:
  注册率: 40%
  试用→付费转化: 25%
  CAC: ¥500

阶段2: API深度使用 (Month 7-12)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户路径:
  付费SaaS → 开发者发现API → 试用API → 集成到产品 → 企业API套餐
转化指标:
  SaaS→API转化: 30%
  API ARPU: ¥5000/月

阶段3: 生态锁定 (Year 2+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户路径:
  API重度使用 → 数据积累 → 产品深度集成 → 私有部署需求 → 战略合作
转化指标:
  API→企业定制: 15%
  企业ARPU: ¥10万/年
```

### 10.2 收入结构演进

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
```

---

## 十一、竞争壁垒构建

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

---

## 十二、Skills与API矩阵

| Skill ID | Skill名称 | API端点 | 定价层级 |
|:--------:|----------|---------|:--------:|
| S01 | jd-generator | POST /v1/jd/generate | Starter+ |
| S02 | resume-parser | POST /v1/resume/parse | Starter+ |
| S03 | candidate-matcher | POST /v1/match/jd-to-candidates | Professional |
| S04 | interview-assistant | POST /v1/interview/start | Professional |
| S05 | outreach-generator | POST /v1/reach/generate | Starter+ |
| S06 | candidate-profile-builder | POST /v1/candidate/profile/build | Professional |
| S07 | job-matcher | GET /v1/candidate/jobs/recommend | Professional |
| S08 | ai-interview-prep | POST /v1/candidate/interview/prep | Starter+ |
| S09 | self-recommendation-writer | POST /v1/candidate/recommendation/generate | Starter+ |
| S10 | application-tracker | GET /v1/candidate/tracker | Free |
| S11 | discovery-radar | POST /v1/discovery/surprise | Enterprise |
| S15-19 | 协作连接器 | POST /feishu/** | Professional |
| S20 | linkedin-connector | POST /v1/connector/linkedin/** | Professional |
| S21 | indeed-connector | GET /v1/connector/indeed/** | Professional |
| S22 | liepin-connector | POST /v1/connector/liepin/** | Enterprise |
| S23 | boss-connector | POST /v1/connector/boss/** | Enterprise |
| S24 | maimai-connector | POST /v1/connector/maimai/** | Professional |
| S25 | zhilian-connector | POST /v1/connector/zhilian/** | Professional |

---

## 十三、开发者生态

### 13.1 开发者门户

```
developer.talentai.pro

┌─────────────────────────────────────────────────────────┐
│  文档中心 (Documentation)                                 │
│  • API Reference (Swagger UI)                            │
│  • SDK下载 (Python/JS/Go/Java)                           │
│  • 快速开始 (5分钟上手)                                   │
│  • 教程 (按场景)                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  API市场 (API Marketplace)                               │
│  • 热门API推荐                                            │
│  • 行业解决方案                                            │
│  • 成功案例                                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  控制台 (Console)                                         │
│  • API Key管理                                           │
│  • 使用量监控                                             │
│  • 日志查询                                               │
└─────────────────────────────────────────────────────────┘
```

### 13.2 SDK支持

```yaml
官方SDK:
  Python:   talentai-python  (pip install talentai)
  JavaScript: talentai-js    (npm install talentai)
  Go:       talentai-go      (go get github.com/talentai/go)
  Java:     talentai-java    (Maven: groupId=ai.talentai)
```

---

*文档版本：v1.0*
*日期：2026年4月22日*
*核心定位：API-First 招聘平台，为开发者生态和未来变现奠定基础*