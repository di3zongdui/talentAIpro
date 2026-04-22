# TalentAI Pro Developer Guide

> Version: 1.0.0 | Last Updated: 2026-04-22

## Quick Start (5 minutes)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/TalentAI-Pro.git
cd TalentAI-Pro

# Install dependencies
pip install -r requirements.txt

# Run the server
python run_server.py
```

### 2. Get API Key

Register at `http://localhost:8000/docs` to get your API key.

### 3. Make Your First Request

```bash
curl -X POST http://localhost:8000/api/v1/candidates \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "张明",
    "email": "zhangming@example.com",
    "title": "AI算法工程师",
    "skills": ["Python", "TensorFlow"]
  }'
```

---

## Authentication

All API requests require the `X-API-Key` header:

```bash
-H "X-API-Key: your-api-key"
```

### API Key Management

- Generate API keys in Dashboard → Settings → API Keys
- Keys are scoped to specific permissions (read/write/admin)
- Rotate keys periodically for security

---

## SDKs

### Python SDK

```bash
pip install talentai-pro
```

```python
from talentai import TalentAI

client = TalentAI(api_key="your-api-key")

# Create candidate
candidate = client.candidates.create({
    "name": "张明",
    "email": "zhangming@example.com",
    "skills": ["Python", "TensorFlow"]
})

# Match candidate to jobs
matches = client.matching.match_candidate(candidate["id"], top_k=5)
```

### JavaScript/TypeScript SDK

```bash
npm install talentai-pro
```

```typescript
import { TalentAI } from 'talentai-pro';

const client = new TalentAI({ apiKey: 'your-api-key' });

const candidate = await client.candidates.create({
  name: '张明',
  email: 'zhangming@example.com',
  skills: ['Python', 'TensorFlow']
});
```

---

## Common Use Cases

### Use Case 1: Find Best Candidates for a Job

```python
# 1. Create or get job
job = client.jobs.create({
    "title": "AI算法专家",
    "skills_required": ["Python", "LLM", "PyTorch"],
    "experience_years_min": 5
})

# 2. Find matching candidates
matches = client.matching.match_job(job["id"], top_k=10)

# 3. Review matches
for match in matches["candidates"]:
    print(f"{match['name']}: {match['match_score']}")
```

### Use Case 2: Track Interview Process

```python
# 1. Create deal
deal = client.deals.create({
    "candidate_id": "cand_001",
    "job_id": "job_001",
    "stage": "interview_scheduled",
    "interview_date": "2026-04-25T14:00:00Z"
})

# 2. Update stage after interview
client.deals.update_stage(deal["id"], {
    "stage": "interview_completed",
    "feedback": "技术面表现优秀"
})

# 3. Add activity
client.deals.add_activity(deal["id"], {
    "activity_type": "email_sent",
    "content": "感谢信已发送"
})
```

### Use Case 3: Generate Outreach Email

```python
# 1. Get candidate intelligence
intel = client.candidates.get_intelligence("cand_001")

# 2. Generate personalized email
email = client.outreach.generate({
    "candidate_id": "cand_001",
    "job_id": "job_001",
    "tone": "professional",
    "include_surprise": True
})

print(email["subject"])
print(email["body"])
```

---

## Webhooks

### Setup

```python
# Register webhook
client.webhooks.create({
    "url": "https://your-server.com/webhook",
    "events": ["deal.stage_changed", "candidate.created"]
})
```

### Verify Webhook Signature

```python
from talentai.webhooks import verify_signature
import hmac
import hashlib

def handle_webhook(request):
    signature = request.headers.get('X-TalentAI-Signature')
    payload = request.body

    if verify_signature(payload, signature, 'your-webhook-secret'):
        # Process event
        event = json.loads(payload)
        print(f"Received: {event['event']}")
    else:
        return 403
```

---

## Error Handling

### Python

```python
from talentai.exceptions import (
    TalentAIError,
    ValidationError,
    NotFoundError,
    RateLimitError
)

try:
    candidate = client.candidates.create(data)
except ValidationError as e:
    print(f"Invalid data: {e.details}")
except NotFoundError as e:
    print(f"Resource not found: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except TalentAIError as e:
    print(f"API error: {e}")
```

### Retry Logic

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=10),
       stop=stop_after_attempt(3))
def call_with_retry():
    return client.candidates.list()
```

---

## Best Practices

### 1. Pagination

Always use pagination for large datasets:

```python
offset = 0
limit = 100

while True:
    candidates = client.candidates.list(limit=limit, offset=offset)
    if not candidates:
        break

    for c in candidates:
        process(c)

    offset += limit
```

### 2. Batch Operations

Use batch APIs for bulk operations:

```python
# Instead of this (slow):
for email in emails:
    client.emails.send(email)

# Do this (fast):
client.emails.send_batch(emails)
```

### 3. Async Operations

For long-running tasks, use async mode:

```python
# Start async operation
job = client.matching.match_job_async("job_001")

# Poll for result
while job.status != "completed":
    job = client.jobs.get(job.id)
    time.sleep(1)

result = job.result
```

### 4. Caching

Cache frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_candidate(candidate_id):
    return client.candidates.get(candidate_id)
```

---

## Testing

### Mock Mode

```python
client = TalentAI(api_key="test-key", mock=True)

# All calls return mock data
candidate = client.candidates.create({"name": "Test"})
assert candidate["id"] == "mock_candidate_001"
```

### Test Examples

```python
import pytest

def test_create_candidate():
    candidate = client.candidates.create({
        "name": "测试候选人",
        "email": "test@example.com"
    })
    assert candidate["id"] is not None
    assert candidate["name"] == "测试候选人"

def test_match_candidate():
    matches = client.matching.match_candidate("cand_001")
    assert len(matches) > 0
    assert all(m["match_score"] > 0 for m in matches)
```

---

## Migration Guide

### v0.x to v1.0

**Breaking Changes:**

1. Base URL changed from `/api` to `/api/v1`
2. Response format now includes `success` field
3. `candidate_id` renamed to `id` in responses
4. Authentication now via `X-API-Key` header (old `Authorization` still works)

**Migration Steps:**

```python
# Old (v0.x)
response = requests.post("/api/candidates", data=data)
candidate = response.json()["candidate"]

# New (v1.0)
response = requests.post("/api/v1/candidates",
                         headers={"X-API-Key": key},
                         json=data)
result = response.json()
candidate = result["data"] if result["success"] else None
```

---

## Support

- **Documentation**: https://docs.talentai-pro.com
- **API Status**: https://status.talentai-pro.com
- **Support Email**: support@talentai-pro.com
- **Community Forum**: https://community.talentai-pro.com
