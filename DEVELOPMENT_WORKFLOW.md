# TalentAI Pro 开发流程规范

> 版本：v1.0
> 生成时间：2026-04-22
> 目的：建立「开发→测试→Git提交→下一阶段」的自动闭环

---

## 一、核心流程

```
┌─────────────────────────────────────────────────────────┐
│                    开发流程闭环                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ① 开发新功能/模块                                       │
│       ↓                                                 │
│  ② 自动运行测试（run_tests.py）                          │
│       ↓                                                 │
│  ③ 测试通过？ ──否──→ 修复错误 → ②                        │
│       ↓ 是                                              │
│  ④ Git add + Git commit                                 │
│       ↓                                                 │
│  ⑤ 开始下一阶段开发                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、Phase 划分

| Phase | 内容 | 优先级 | 状态 |
|-------|------|--------|------|
| Phase 1 | 核心匹配引擎v1 + API层 + 基础Skills | P0 | ✅ 完成 |
| **Phase 2** | **Skills升级：JD Intelligence v2.0 + Candidate Intelligence v2.0 + Discovery Radar** | **P0** | 🚧 进行中 |
| Phase 3 | Skills升级：Smart Outreach + Deal Tracker | P1 | 待开始 |
| Phase 4 | AI面试引擎（海纳AI/HireVue + MiniMax-M2.7） | P1 | 待开始 |
| Phase 5 | 外部平台连接器（LinkedIn/GitHub/猎聘） | P2 | 待开始 |

---

## 三、Phase 2 开发清单

### P0-1: JD Intelligence Engine v2.0

**当前能力：** 文本解析 → 结构化字段

**升级后能力：**
- [ ] 隐含偏好挖掘（JD没写但暗示的东西）
- [ ] 公司超预期亮点注入
- [ ] 候选人稀缺性评估
- [ ] 薪资竞争力校准
- [ ] 匹配难度评级

**输出文件：** `TalentAI_Pro/skills/jd_parser/jd_intelligence_v2.py`

### P0-2: Candidate Intelligence Engine v2.0

**当前能力：** 解析简历 → 基本画像

**升级后能力：**
- [ ] 全网背景交叉验证（GitHub/LinkedIn/脉脉）
- [ ] 超预期亮点发现（开源/论文/创业）
- [ ] 薪资/职级预测
- [ ] 风险预警（频繁跳槽/职业断层）
- [ ] 求职意向推测

**输出文件：** `TalentAI_Pro/skills/resume_parser/candidate_intelligence_v2.py`

### P0-3: Discovery Radar

**功能：** 双向背景尽调

**候选人侧：**
- [ ] LinkedIn 职位轨迹
- [ ] GitHub 项目活跃度
- [ ] 脉脉行业口碑
- [ ] 论文/专利

**公司侧：**
- [ ] 融资信息
- [ ] 团队背景
- [ ] 舆情分析

**输出文件：** `TalentAI_Pro/skills/discovery_radar/radar.py`

---

## 四、测试要求

### 测试脚本位置
```
TalentAI_Pro/tests/run_tests.py
```

### 测试通过标准
- 所有测试用例 PASS
- 无语法错误
- 无运行时异常

### 运行方式
```bash
python TalentAI_Pro/tests/run_tests.py
```

---

## 五、Git 提交规范

### 提交格式
```
<type>: <简短描述>

<详细说明（可选）>
```

### Type 类型
- `feat:` 新功能
- `fix:` 修复错误
- `test:` 测试相关
- `docs:` 文档更新
- `refactor:` 重构

### 示例
```
feat: Phase 2 - JD Intelligence Engine v2.0 完成

- 新增隐含偏好挖掘功能
- 新增薪资竞争力校准
- 新增匹配难度评级
- 测试全部通过
```

---

## 六、质量门禁

| 检查项 | 标准 | 责任人 |
|--------|------|--------|
| 功能测试 | 100%通过 | CI自动 |
| 语法检查 | 无错误 | CI自动 |
| 文档更新 | 每个Phase更新一次 | 开发者 |
| Git提交 | 每个功能一次 | 开发者 |

---

## 七、版本记录

| 版本 | 日期 | 内容 |
|------|------|------|
| v1.0 | 2026-04-22 | 初始版本，建立开发流程闭环 |
