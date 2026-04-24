# 飞书同步数据源插件
# 同步飞书日历/文档/Bitable数据

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from . import TalentAIPlugin, PluginType, PluginStatus, HeartbeatResult, DataItem

logger = logging.getLogger(__name__)


class FeishuSyncPlugin(TalentAIPlugin):
    """飞书同步数据源插件"""

    def __init__(self, app_id: str = None, app_secret: str = None):
        super().__init__("feishu_sync", PluginType.DATA_SOURCE)
        self.app_id = app_id or self.config.get("app_id", "")
        self.app_secret = app_secret or self.config.get("app_secret", "")
        self.access_token = self.config.get("access_token", "")
        self.token_expires_at = self.config.get("token_expires_at")
        self._use_mock = not bool(self.app_id)

        self._calendar_events = []
        self._documents = []
        self._bitable_records = []

    async def initialize(self) -> bool:
        """初始化插件"""
        if self._use_mock:
            logger.info("FeishuSyncPlugin: Running in mock mode")
            self._init_mock_data()
            return True

        success = await self._get_access_token()
        if not success:
            self._use_mock = True
            self._init_mock_data()
        return True

    async def heartbeat(self) -> HeartbeatResult:
        """执行心跳"""
        if self._use_mock:
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.SUCCESS,
                items_added=2,
                metadata={"mode": "mock", "events": len(self._calendar_events)}
            )

        try:
            new_events = await self._sync_calendar()
            new_docs = await self._sync_documents()
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.SUCCESS,
                items_added=len(new_events) + len(new_docs),
                metadata={"new_events": len(new_events), "new_docs": len(new_docs)}
            )
        except Exception as e:
            logger.error(f"FeishuSyncPlugin heartbeat error: {e}")
            return HeartbeatResult(plugin_name=self.name, status=PluginStatus.FAILED, error_message=str(e))

    async def fetch_data(self, since: Optional[datetime] = None) -> List[DataItem]:
        """获取数据条目"""
        items = []
        for event in self._calendar_events:
            items.append(DataItem(id=f"feishu_event_{event['event_id']}", type="calendar_event",
                                  source=self.name, data=event, timestamp=datetime.now()))
        for doc in self._documents:
            items.append(DataItem(id=f"feishu_doc_{doc['doc_id']}", type="document",
                                  source=self.name, data=doc, timestamp=datetime.now()))
        for record in self._bitable_records:
            items.append(DataItem(id=f"feishu_bitable_{record['record_id']}", type="bitable_record",
                                  source=self.name, data=record, timestamp=datetime.now()))
        return items

    async def _get_access_token(self) -> bool:
        """获取Access Token"""
        try:
            # 实际应该调用飞书API获取tenant_access_token
            self.access_token = f"feishu_token_{datetime.now().timestamp()}"
            self.token_expires_at = datetime.now() + timedelta(hours=2)
            return True
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return False

    async def _sync_calendar(self) -> List[Dict]:
        """同步日历事件"""
        # 模拟获取近期的日历事件
        return []

    async def _sync_documents(self) -> List[Dict]:
        """同步文档"""
        return []

    def _init_mock_data(self):
        """初始化Mock数据"""
        self._calendar_events = [
            {"event_id": "evt_001", "title": "张明 - 前端面试", "start_time": "2024-03-15 10:00",
             "end_time": "2024-03-15 11:00", "attendees": ["李经理", "张明"],
             "location": "线上", "type": "interview"},
            {"event_id": "evt_002", "title": "李华 - 产品经理面试", "start_time": "2024-03-15 14:00",
             "end_time": "2024-03-15 15:00", "attendees": ["王总监", "李华"],
             "location": "北京办公室", "type": "interview"},
            {"event_id": "evt_003", "title": "候选人推荐评审会", "start_time": "2024-03-16 09:00",
             "end_time": "2024-03-16 10:00", "attendees": ["CGL团队"],
             "location": "会议室A", "type": "meeting"}
        ]
        self._documents = [
            {"doc_id": "doc_001", "title": "CGL-前端岗位JD-v2.1", "type": "doc",
             "url": "https://feishu.cn/doc/doc_001", "last_modified": "2024-03-10"},
            {"doc_id": "doc_002", "title": "候选人评估模板", "type": "doc",
             "url": "https://feishu.cn/doc/doc_002", "last_modified": "2024-03-08"}
        ]
        self._bitable_records = [
            {"record_id": "rec_001", "table": "候选人库", "name": "赵磊",
             "status": "面试中", "last_modified": "2024-03-12"},
            {"record_id": "rec_002", "table": "职位库", "name": "前端技术专家",
             "status": "招聘中", "last_modified": "2024-03-10"}
        ]

    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return {
            "connected": bool(self.access_token) or self._use_mock,
            "use_mock": self._use_mock,
            "data_counts": {
                "calendar_events": len(self._calendar_events),
                "documents": len(self._documents),
                "bitable_records": len(self._bitable_records)
            }
        }
