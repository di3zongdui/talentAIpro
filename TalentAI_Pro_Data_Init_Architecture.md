# TalentAI Pro 数据初始化与心跳更新架构

> **Version:** 1.0 | **Date:** 2026-04-23 | **Author:** TalentAI Pro Architecture Team

---

## 1. 核心问题定义

### 当前痛点

| 问题 | 影响 |
|------|------|
| 简历散落在本地各个文件夹 | 无法统一管理、重复简历难以识别 |
| 职位信息需手动录入 | 效率低、易出错、时效性差 |
| 外部渠道数据需手动搬运 | 浪费时间、数据陈旧 |
| 候选人/职位变更无法及时感知 | 错失最佳联系时机 |

### 目标

```
┌─────────────────────────────────────────────────────────────────┐
│                    数据初始化 + 心跳更新                         │
├─────────────────────────────────────────────────────────────────┤
│  本地文件夹 ──────┐                                             │
│                   │                                             │
│  猎聘/拉勾 API ───┼──→ 统一数据层 ──→ TalentAI Pro Skills ──→ 用户 │
│                   │       (心跳同步)                            │
│  飞书/Bitable ───┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据源分类

### 2.1 本地渠道

| 渠道 | 格式 | 触发方式 |
|------|------|---------|
| **简历文件夹** | PDF/DOCX/XLSX/CSV/TXT | 手动/定时扫描 |
| **企业Bitable** | 多维表格 | 增量同步 |
| **飞书云文档** | 文档API | 增量同步 |
| **本地数据库** | SQLite/PostgreSQL | 定时拉取 |

### 2.2 互联网渠道

| 渠道 | 数据类型 | 更新方式 |
|------|---------|---------|
| **猎聘** | 简历库/职位库 | API轮询 + Webhook |
| **Boss直聘** | 候选人/职位 | Cookie模拟 |
| **领英** | 人脉网络/公司简介 | API(需认证) |
| **拉勾** | 职位/候选人 | API轮询 |
| **脉脉** | 职场社交数据 | API轮询 |

---

## 3. 数据初始化流程

### 3.1 职位(JD)初始化

```
┌──────────────────────────────────────────────────────────────────┐
│                      JD初始化流程                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ 本地文件夹   │    │ 飞书/Bitable│    │ 互联网渠道   │         │
│  │ (PDF/DOCX)  │    │ (多维表格)  │    │ (猎聘API)   │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │   JD Parser     │                           │
│                   │ (Group Intel    │                           │
│                   │  Hub v2)        │                           │
│                   └────────┬────────┘                           │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │ JD Intelligence │                           │
│                   │ Engine v2      │                           │
│                   │ • 隐含偏好挖掘  │                           │
│                   │ • 稀缺性评估    │                           │
│                   │ • 薪资校准     │                           │
│                   │ • 难度评级     │                           │
│                   └────────┬────────┘                           │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │   职位数据库     │                           │
│                   │ (Bitable/DB)   │                           │
│                   └─────────────────┘                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 简历初始化

```
┌──────────────────────────────────────────────────────────────────┐
│                      简历初始化流程                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ 本地文件夹   │    │ 猎聘简历库  │    │ 领英Profile │         │
│  │ (PDF/DOCX)  │    │ (API导出)   │    │ (爬虫/API)  │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │ Resume Parser   │                           │
│                   │ (Group Intel    │                           │
│                   │  Hub v2)        │                           │
│                   │ • Text Parser   │                           │
│                   │ • Image Parser  │                           │
│                   │ • PDF Parser   │                           │
│                   │ • Voice Parser  │                           │
│                   └────────┬────────┘                           │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │ Candidate Intel │                           │
│                   │ Engine v2       │                           │
│                   │ • 全网背景调查   │                           │
│                   │ • 超预期发现    │                           │
│                   │ • 风险预警     │                           │
│                   │ • 薪资预测     │                           │
│                   └────────┬────────┘                           │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │  候选人数据库    │                           │
│                   │ (Bitable/DB)   │                           │
│                   └─────────────────┘                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. 心跳更新架构

### 4.1 三层心跳机制

```
┌─────────────────────────────────────────────────────────────────┐
│                      心跳更新三层架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  L1: 实时层 (事件驱动)                                    │    │
│  │  ├── 飞书文档变更 → Webhook → 即时更新                    │    │
│  │  ├── Bitable记录变更 → Webhook → 即时更新                │    │
│  │  └── 猎聘简历投递 → 消息队列 → 即时通知                   │    │
│  │  时延: < 1分钟                                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  L2: 增量层 (定时心跳)                                    │    │
│  │  ├── 每15分钟: 检查本地文件夹新增/删除文件                │    │
│  │  ├── 每30分钟: 猎聘/Boss 新职位同步                      │    │
│  │  └── 每小时:   候选人状态变更检查                        │    │
│  │  时延: 15-60分钟                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  L3: 全量层 (定期维护)                                    │    │
│  │  ├── 每日凌晨: 全量数据健康检查                          │    │
│  │  ├── 每周:   去重/合并/归档                              │    │
│  │  └── 每月:   历史数据归档                                │    │
│  │  时延: 1天-1月                                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 心跳调度器设计

```python
# heartbeat_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

class TalentAIHeartbeatScheduler:
    """TalentAI Pro 心跳调度器"""

    def __init__(self, data_service):
        self.data_service = data_service
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)

    def start(self):
        """启动所有心跳任务"""

        # L1: 实时层 - 启动WebSocket/长连接监听
        self._start_realtime_listeners()

        # L2: 增量层 - 定时心跳
        self.scheduler.add_job(
            self._check_local_folders,
            'interval',
            minutes=15,
            id='check_local_folders',
            name='本地文件夹变更检查'
        )

        self.scheduler.add_job(
            self._sync_external_jd,
            'interval',
            minutes=30,
            id='sync_external_jd',
            name='外部JD同步'
        )

        self.scheduler.add_job(
            self._check_candidate_updates,
            'interval',
            minutes=60,
            id='check_candidate_updates',
            name='候选人状态检查'
        )

        # L3: 全量层 - 定期维护
        self.scheduler.add_job(
            self._daily_health_check,
            'cron',
            hour=2,  # 凌晨2点
            id='daily_health_check',
            name='每日健康检查'
        )

        self.scheduler.add_job(
            self._weekly_dedup,
            'cron',
            day_of_week='mon',  # 每周一
            hour=3,
            id='weekly_dedup',
            name='每周去重合并'
        )

        self.scheduler.start()
        self.logger.info("TalentAI心跳调度器已启动")

    def _start_realtime_listeners(self):
        """启动实时监听器"""
        # 飞书Webhook监听
        self.data_service.feishu.on_document_change(self._on_feishu_doc_change)
        # Bitable Webhook监听
        self.data_service.bitable.on_record_change(self._on_bitable_record_change)
        # 猎聘消息队列监听
        self.data_service.liepin.on_message(self._on_liepin_message)

    def _on_feishu_doc_change(self, event):
        """飞书文档变更回调"""
        self.logger.info(f"飞书文档变更: {event.doc_id}")
        # 触发JD重新解析
        self.data_service.refresh_jd(event.doc_id)
        # 推送更新通知
        self.data_service.notify_update('jd', event.doc_id)

    def _on_bitable_record_change(self, event):
        """Bitable记录变更回调"""
        self.logger.info(f"Bitable记录变更: {event.table_id}")
        # 增量同步
        self.data_service.sync_incremental(event.table_id, event.record_id)
</python>

### 4.3 增量同步策略

```python
class IncrementalSyncStrategy:
    """增量同步策略"""

    # 同步状态跟踪
    SYNC_STATE = {
        'last_sync_time': {},      # 各数据源最后同步时间
        'last_sync_hash': {},      # 文件内容hash
        'deleted_items': [],       # 已删除项目
        'pending_updates': []      # 待处理更新
    }

    def should_sync(self, source: str, item_id: str) -> bool:
        """判断是否需要同步"""
        last_time = self.SYNC_STATE['last_sync_time'].get(source)
        if not last_time:
            return True  # 首次同步

        # 检查是否有更新
        item = self.data_service.get_item(source, item_id)
        if not item:
            # 项目已删除，标记
            self.SYNC_STATE['deleted_items'].append((source, item_id))
            return False

        return item['updated_at'] > last_time

    def sync_incremental(self, source: str):
        """执行增量同步"""
        items = self.data_service.get_items(source)

        for item in items:
            if self.should_sync(source, item['id']):
                self._process_update(source, item)

        # 处理已删除项目
        self._process_deletions(source)

        # 更新同步时间
        self.SYNC_STATE['last_sync_time'][source] = datetime.now()

    def _process_deduplication(self):
        """处理去重"""
        candidates = self.data_service.get_all_candidates()

        # 按手机号/邮箱/姓名+公司分组
        groups = defaultdict(list)
        for c in candidates:
            key = self._generate_dedup_key(c)
            groups[key].append(c)

        # 合并重复项
        for key, items in groups.items():
            if len(items) > 1:
                merged = self._merge_candidates(items)
                for item in items:
                    if item['id'] != merged['id']:
                        self.data_service.mark_duplicate(item['id'], merged['id'])
```

---

## 5. 数据存储设计

### 5.1 多维表格结构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Bitable 数据模型                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   候选人库       │    │   职位库         │                    │
│  ├─────────────────┤    ├─────────────────┤                    │
│  │ id              │    │ id              │                    │
│  │ name            │    │ title           │                    │
│  │ phone           │    │ company         │                    │
│  │ email           │    │ skills_required │                    │
│  │ skills          │    │ experience_min  │                    │
│  │ experience_years│    │ salary_range    │                    │
│  │ education       │    │ location        │                    │
│  │ current_company │    │ status          │                    │
│  │ current_title   │    │ source          │                    │
│  │ status          │    │ created_at      │                    │
│  │ source          │    │ updated_at      │                    │
│  │ resume_url      │    │ resume_url      │                    │
│  │ ai_profile      │    │ ai_analysis     │                    │
│  │ created_at      │    │ sync_status     │                    │
│  │ updated_at      │    └─────────────────┘                    │
│  └─────────────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   交易跟踪表     │    │   同步日志表     │                    │
│  ├─────────────────┤    ├─────────────────┤                    │
│  │ id              │    │ id              │                    │
│  │ candidate_id    │    │ source          │                    │
│  │ job_id          │    │ action          │                    │
│  │ stage           │    │ item_id         │                    │
│  │ probability     │    │ status          │                    │
│  │ owner           │    │ timestamp       │                    │
│  │ next_action     │    │ details         │                    │
│  │ created_at      │    └─────────────────┘                    │
│  └─────────────────┘                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 本地缓存策略

```
┌─────────────────────────────────────────────────────────────────┐
│                      数据分层存储                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   热数据 (Hot)     ──→   内存缓存 (Redis)  ──→  最近7天活跃数据 │
│   温数据 (Warm)   ──→   本地SSD存储       ──→  7-30天数据      │
│   冷数据 (Cold)   ──→   对象存储 (S3)     ──→  30天+历史归档    │
│                                                                 │
│   索引 (Index)    ──→   SQLite/ES        ──→  快速检索        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 互联网渠道集成

### 6.1 渠道优先级

| 优先级 | 渠道 | 集成方式 | 数据质量 | 更新频率 |
|--------|------|---------|---------|---------|
| P0 | **猎聘** | 官方API | ⭐⭐⭐⭐⭐ | 实时 |
| P0 | **Boss直聘** | Cookie+API | ⭐⭐⭐⭐ | 小时级 |
| P1 | **领英** | API(需会员) | ⭐⭐⭐⭐⭐ | 每日 |
| P1 | **脉脉** | API | ⭐⭐⭐ | 每日 |
| P2 | **拉勾** | API | ⭐⭐⭐⭐ | 小时级 |
| P2 | **智联招聘** | 爬虫 | ⭐⭐⭐ | 每日 |

### 6.2 猎聘API集成示例

```python
class LiepinConnector:
    """猎聘数据连接器"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.liepin.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_resume_list(self, updated_after: datetime = None) -> List[dict]:
        """获取简历列表"""
        params = {
            "page_size": 100,
            "sort_by": "updated_at",
            "order": "desc"
        }
        if updated_after:
            params["updated_after"] = updated_after.isoformat()

        response = requests.get(
            f"{self.base_url}/v1/resumes",
            headers=self.headers,
            params=params
        )

        return self._parse_response(response)

    def get_resume_detail(self, resume_id: str) -> dict:
        """获取简历详情"""
        response = requests.get(
            f"{self.base_url}/v1/resumes/{resume_id}",
            headers=self.headers
        )
        return self._parse_response(response)

    def subscribe_webhook(self, callback_url: str, events: List[str]):
        """订阅Webhook"""
        payload = {
            "callback_url": callback_url,
            "events": events  # ["resume.created", "resume.updated"]
        }
        response = requests.post(
            f"{self.base_url}/v1/webhooks",
            headers=self.headers,
            json=payload
        )
        return response.json()
```

---

## 7. 监控与告警

### 7.1 健康检查指标

```python
HEALTH_METRICS = {
    # 数据 freshness
    "jd_freshness_hours": 24,        # JD最后更新不超过24小时
    "candidate_freshness_days": 7,   # 候选人最后更新不超过7天

    # 数据质量
    "duplicate_rate_threshold": 0.05,  # 重复率不超过5%
    "missing_field_rate": 0.1,          # 缺失字段不超过10%

    # 系统健康
    "sync_success_rate": 0.95,         # 同步成功率不低于95%
    "heartbeat_interval_sec": 300,     # 心跳间隔不超过5分钟
}
```

### 7.2 告警规则

| 告警级别 | 条件 | 通知方式 |
|---------|------|---------|
| 🔴 Critical | 同步服务宕机 > 5分钟 | 短信+电话 |
| 🟠 High | 连续3次同步失败 | 钉钉/飞书 |
| 🟡 Medium | 数据新鲜度超标 | 邮件 |
| 🟢 Low | 重复率超标 | 日志记录 |

---

## 8. 实施路线图

### Phase 1: 本地数据初始化 (Week 1-2)

```
□ 本地文件夹扫描器
□ 简历解析器（PDF/DOCX/XLSX/CSV/TXT）
□ Bitable数据导入
□ 飞书文档同步
```

### Phase 2: 单一互联网渠道集成 (Week 3-4)

```
□ 猎聘API对接
□ Webhook实时推送
□ 增量同步机制
```

### Phase 3: 心跳监控系统 (Week 5-6)

```
□ 心跳调度器
□ 健康检查
□ 告警系统
□ 数据质量仪表板
```

### Phase 4: 多渠道扩展 (Week 7-8)

```
□ Boss直聘集成
□ 领英集成
□ 拉勾集成
□ 数据去重引擎
```

---

## 9. 总结

```
┌─────────────────────────────────────────────────────────────────┐
│                      核心设计原则                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 本地优先 ── 先充分利用本地数据，再拓展互联网渠道             │
│  2. 增量同步 ── 只同步变化数据，避免重复处理                     │
│  3. 事件驱动 ── Webhook优先，轮询兜底                           │
│  4. 可观测性 ── 完整日志+监控+告警，确保数据可信                 │
│  5. 容错设计 ── 失败重试+幂等操作+状态跟踪                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**下一步行动：**

1. **立即可做**：配置本地简历文件夹路径，启动初始扫描
2. **本周**：集成猎聘API（若有账号权限）
3. **下周**：部署心跳调度器，建立监控告警

---

*Document Version: 1.0 | Last Updated: 2026-04-23*
