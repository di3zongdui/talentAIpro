# Interview Agent - 面试Agent

## 概述

Interview Agent 替代面试官执行结构化面试，包括：
- 技术问题生成
- 行为面试问题（STAR法则）
- 实时评估与评分
- 结构化反馈报告

## 核心能力

### 1. 问题生成 (Question Generator)

```python
# 输入：JD + 候选人简历
# 输出：结构化面试问题列表

questions = {
    "technical": [
        {
            "skill": "Python",
            "level": "senior",
            "question": "请解释Python中的GIL是什么，以及它对多线程的影响？",
            "expected_keywords": ["Global Interpreter Lock", "线程安全"],
            "difficulty": 4
        }
    ],
    "behavioral": [
        {
            "category": "leadership",
            "question": "请描述一次你带领团队克服重大技术挑战的经历",
            "star_framework": True
        }
    ]
}
```

### 2. 评估引擎 (Evaluation Engine)

```python
# 评估维度
evaluation_dimensions = [
    "technical_depth",      # 技术深度
    "problem_solving",      # 问题解决能力
    "communication",        # 沟通表达
    "culture_fit",          # 文化匹配
    "growth_potential"      # 成长潜力
]

# 评分标准：1-5分
score = {
    "dimension": "technical_depth",
    "score": 4,
    "evidence": "深入理解并发编程原理...",
    "keywords_matched": ["GIL", "线程池", "异步"]
}
```

### 3. 报告生成 (Report Generator)

```python
# 结构化面试报告
interview_report = {
    "candidate_id": "uuid",
    "interview_id": "uuid",
    "overall_score": 4.2,
    "recommendation": "强烈推荐",
    "dimension_scores": {
        "technical_depth": 4.5,
        "problem_solving": 4.0,
        "communication": 4.2,
        "culture_fit": 4.0,
        "growth_potential": 4.3
    },
    "strengths": [...],
    "concerns": [...],
    "detailed_evaluation": {...}
}
```

## 数据流

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ JD Parser   │ →  │ Question Generator│ →  │ Interview Flow │
│  (输入JD)   │    │   (生成问题)     │    │   (面试流程)    │
└─────────────┘    └──────────────────┘    └────────┬────────┘
                                                     │
                                                     ↓
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Final Report│ ←  │  Report Generator│ ←  │ Evaluation Eng  │
│  (最终报告)  │    │    (生成报告)    │    │    (评估)       │
└─────────────┘    └──────────────────┘    └─────────────────┘
```

## API 端点

```
POST /api/v2/interviews/generate-questions
     - 输入: job_description, candidate_profile
     - 输出: structured_questions

POST /api/v2/interviews/{id}/evaluate
     - 输入: question_id, answer
     - 输出: evaluation_result

POST /api/v2/interviews/{id}/complete
     - 输入: interview_id
     - 输出: final_report

GET  /api/v2/interviews/{id}/report
     - 输出: interview_report
```

## 技术栈

- **LLM**: GPT-4 / Claude 用于问题生成和评估
- **向量数据库**: 存储历史面试问题用于复用
- **评估模型**: 结构化评分 + 自然语言反馈

## 状态机

```
[CREATED] → [QUESTIONS_GENERATED] → [IN_PROGRESS] → [COMPLETED]
                              ↓
                         [CANCELLED]
```