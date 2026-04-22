# TalentAI Pro API Reference

> Version: 1.0.0 | Base URL: `http://localhost:8000/api/v1`

## Overview

TalentAI Pro provides a RESTful API for AI-powered recruitment intelligence. The API follows OpenAPI 3.0 conventions with JSON request/response bodies.

**Authentication**: API Key via `X-API-Key` header

---

## Base Request/Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [...]
  }
}
```

---

## Candidates API

### Create Candidate

```
POST /candidates
```

**Request Body:**

```json
{
  "name": "张明",
  "email": "zhangming@example.com",
  "phone": "+86-138-0000-0000",
  "title": "高级算法工程师",
  "company": "字节跳动",
  "skills": ["Python", "TensorFlow", "PyTorch", "LLM"],
  "experience_years": 8,
  "education": "硕士",
  "school": "清华大学",
  "current_salary": 1500000,
  "expected_salary": 2000000,
  "location": "北京",
  "current_status": "actively_looking",
  "source": "LinkedIn",
  "notes": "有NLP和大模型经验"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "cand_001",
    "name": "张明",
    "email": "zhangming@example.com",
    "created_at": "2026-04-22T10:00:00Z"
  }
}
```

### Get Candidate

```
GET /candidates/{id}
```

### List Candidates

```
GET /candidates?status=active&limit=20&offset=0
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (active/inactive/placed) |
| skills | string | Comma-separated skills to filter |
| location | string | Filter by location |
| limit | int | Max results (default: 20, max: 100) |
| offset | int | Pagination offset |

### Update Candidate

```
PATCH /candidates/{id}
```

### Delete Candidate

```
DELETE /candidates/{id}
```

---

## Jobs API

### Create Job

```
POST /jobs
```

**Request Body:**

```json
{
  "title": "AI算法专家",
  "company": "某头部AI公司",
  "location": "北京",
  "department": "AI Lab",
  "salary_range": {"min": 1000000, "max": 2000000, "currency": "CNY"},
  "requirements": [
    "5年以上AI/ML算法经验",
    "扎实的深度学习基础",
    "有大模型训练经验优先"
  ],
  "responsibilities": [
    "负责大模型算法研发",
    "带领技术团队",
    "推动AI技术落地"
  ],
  "skills_required": ["Python", "PyTorch", "LLM", "分布式训练"],
  "experience_years_min": 5,
  "education_min": "硕士",
  "remote_policy": "hybrid",
  "source": "客户直接委托",
  "priority": "high"
}
```

### Get Job

```
GET /jobs/{id}
```

### List Jobs

```
GET /jobs?status=open&priority=high&limit=20
```

### Update Job

```
PATCH /jobs/{id}
```

### Delete Job

```
DELETE /jobs/{id}
```

---

## Matching API

### Match Candidate to Jobs

```
POST /matching/candidate/{candidate_id}
```

**Request Body:**

```json
{
  "top_k": 5,
  "threshold": 0.6,
  "include_reason": true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "candidate_id": "cand_001",
    "matches": [
      {
        "job_id": "job_001",
        "job_title": "AI算法专家",
        "match_score": 0.85,
        "match_reason": "技能匹配度95%，经验匹配度90%",
        "surprise_score": 0.72,
        "surprise_highlights": [
          "在大厂有LLM实际落地经验",
          "发表过顶会论文"
        ]
      }
    ],
    "total_candidates_matched": 5
  }
}
```

### Match Job to Candidates

```
POST /matching/job/{job_id}
```

### Batch Match

```
POST /matching/batch
```

**Request Body:**

```json
{
  "candidate_ids": ["cand_001", "cand_002"],
  "job_id": "job_001",
  "top_k_per_candidate": 1
}
```

---

## Deals API

### Create Deal

```
POST /deals
```

**Request Body:**

```json
{
  "candidate_id": "cand_001",
  "job_id": "job_001",
  "stage": "interview_scheduled",
  "interview_date": "2026-04-25T14:00:00Z",
  "interviewer": "李总",
  "notes": "第一轮面试，技术面"
}
```

### Update Deal Stage

```
PATCH /deals/{id}/stage
```

**Request Body:**

```json
{
  "stage": "offer_extended",
  "salary_offered": 1800000,
  "notes": "已发送offer，等待回复"
}
```

### Get Deal

```
GET /deals/{id}
```

### List Deals

```
GET /deals?status=active&stage=offer_extended
```

### Add Deal Activity

```
POST /deals/{id}/activities
```

**Request Body:**

```json
{
  "activity_type": "email_opened",
  "metadata": {"opened_at": "2026-04-22T15:30:00Z"}
}
```

### Get Deal Timeline

```
GET /deals/{id}/timeline
```

---

## Analytics API

### Get Pipeline Stats

```
GET /analytics/pipeline
```

**Response:**

```json
{
  "success": true,
  "data": {
    "total_deals": 45,
    "by_stage": {
      "sourcing": 10,
      "screening": 8,
      "interview_scheduled": 12,
      "interview_completed": 7,
      "offer_extended": 5,
      "hired": 3
    },
    "conversion_rates": {
      "sourcing_to_screening": 0.80,
      "screening_to_interview": 0.75,
      "interview_to_offer": 0.71,
      "offer_to_hired": 0.60
    }
  }
}
```

### Get Consultant Performance

```
GET /analytics/consultants/{consultant_id}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request body |
| UNAUTHORIZED | 401 | Missing or invalid API key |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

---

## Rate Limits

| Plan | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Free | 60 | 1,000 |
| Pro | 300 | 10,000 |
| Enterprise | 1,000 | Unlimited |

---

## Webhooks

Subscribe to events for real-time updates:

```
POST /webhooks
```

**Event Types:**

- `candidate.created`
- `candidate.updated`
- `deal.stage_changed`
- `deal.activity_added`
- `match.completed`

**Payload:**

```json
{
  "event": "deal.stage_changed",
  "timestamp": "2026-04-22T15:30:00Z",
  "data": {
    "deal_id": "deal_001",
    "old_stage": "interview_scheduled",
    "new_stage": "interview_completed"
  }
}
```
