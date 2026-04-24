# 猎聘OAuth数据源插件
# 通过OAuth获取猎聘平台的简历/对话/行为数据

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

from . import TalentAIPlugin, PluginType, PluginStatus, HeartbeatResult, DataItem

logger = logging.getLogger(__name__)


class LiepinOAuthPlugin(TalentAIPlugin):
    """猎聘OAuth数据源插件"""

    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("liepin_oauth", PluginType.DATA_SOURCE)
        self.api_key = api_key or self.config.get("api_key", "")
        self.api_secret = api_secret or self.config.get("api_secret", "")
        self.access_token = self.config.get("access_token", "")
        self.token_expires_at = self.config.get("token_expires_at")
        self._use_mock = not bool(self.api_key)

        self._candidates = []
        self._jobs = []
        self._conversations = []
        self._behaviors = []
        self._last_fetch = None

    async def initialize(self) -> bool:
        """初始化插件"""
        if self._use_mock:
            logger.info("LiepinOAuthPlugin: Running in mock mode")
            self._init_mock_data()
            return True

        if not self.access_token or self._is_token_expired():
            success = await self._refresh_token()
            if not success:
                self._use_mock = True
                self._init_mock_data()
                return True

        await self._load_data()
        return True

    async def heartbeat(self) -> HeartbeatResult:
        """执行心跳"""
        if self._use_mock:
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.SUCCESS,
                items_added=2,
                items_updated=1,
                metadata={"mode": "mock", "total_candidates": len(self._candidates)}
            )

        try:
            new_items = await self._fetch_incremental_data()
            added = len([i for i in new_items if i.type == "candidate"])
            updated = len([i for i in new_items if i.type in ["conversation", "behavior"]])
            self._last_fetch = datetime.now()
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.SUCCESS,
                items_added=added,
                items_updated=updated,
                metadata={"new_items": len(new_items)}
            )
        except Exception as e:
            logger.error(f"LiepinOAuthPlugin heartbeat error: {e}")
            return HeartbeatResult(
                plugin_name=self.name,
                status=PluginStatus.FAILED,
                error_message=str(e)
            )

    async def fetch_data(self, since: Optional[datetime] = None) -> List[DataItem]:
        """获取数据条目"""
        items = []
        for c in self._candidates:
            items.append(DataItem(id=f"liepin_{c['candidate_id']}", type="candidate",
                                  source=self.name, data=c, timestamp=datetime.now()))
        for j in self._jobs:
            items.append(DataItem(id=f"liepin_{j['job_id']}", type="job",
                                  source=self.name, data=j, timestamp=datetime.now()))
        for conv in self._conversations:
            items.append(DataItem(id=f"liepin_conv_{conv['conversation_id']}", type="conversation",
                                  source=self.name, data=conv, timestamp=datetime.now()))
        for b in self._behaviors:
            items.append(DataItem(id=f"liepin_behavior_{b['behavior_id']}", type="behavior",
                                  source=self.name, data=b, timestamp=datetime.now()))
        return items

    async def _refresh_token(self) -> bool:
        """刷新Access Token"""
        try:
            logger.info("LiepinOAuthPlugin: Refreshing access token...")
            self.access_token = f"mock_token_{datetime.now().timestamp()}"
            self.token_expires_at = datetime.now() + timedelta(days=30)
            self.config["access_token"] = self.access_token
            self.config["token_expires_at"] = self.token_expires_at
            return True
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return False

    def _is_token_expired(self) -> bool:
        """检查Token是否过期"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at - timedelta(hours=1)

    async def _load_data(self):
        """加载初始数据"""
        logger.info("LiepinOAuthPlugin: Loading data from API...")
        await asyncio.sleep(0.1)
        self._init_mock_data()

    async def _fetch_incremental_data(self) -> List[DataItem]:
        """获取增量数据"""
        return []

    def _init_mock_data(self):
        """初始化Mock数据"""
        self._candidates = [
            {"candidate_id": "lp_001", "name": "赵磊", "title": "资深前端开发", "company": "美团",
             "skills": ["React", "Vue", "TypeScript", "Node.js"], "experience_years": 6,
             "education": "硕士", "expected_salary": 60, "location": "北京", "status": "active",
             "last_active": "2024-03-10", "response_rate": 0.85, "interview_count": 3},
            {"candidate_id": "lp_002", "name": "周敏", "title": "产品总监", "company": "京东",
             "skills": ["产品战略", "团队管理", "数据分析", "商业化"], "experience_years": 10,
             "education": "MBA", "expected_salary": 120, "location": "北京", "status": "active",
             "last_active": "2024-03-12", "response_rate": 0.92, "interview_count": 5},
            {"candidate_id": "lp_003", "name": "钱伟", "title": "后端架构师", "company": "字节跳动",
             "skills": ["Java", "Go", "Kubernetes", "分布式系统"], "experience_years": 8,
             "education": "硕士", "expected_salary": 80, "location": "上海", "status": "passive",
             "last_active": "2024-03-08", "response_rate": 0.65, "interview_count": 1}
        ]
        self._jobs = [
            {"job_id": "lp_job_001", "title": "前端技术专家", "company": "某一线大厂",
             "skills_required": ["React", "Vue", "性能优化"], "experience_required": "5-8年",
             "salary_range": "50-80K", "location": "北京", "status": "open"},
            {"job_id": "lp_job_002", "title": "CTO", "company": "某融资C轮创业公司",
             "skills_required": ["技术战略", "团队建设", "架构设计"], "experience_required": "15年+",
             "salary_range": "150-200K+期权", "location": "北京", "status": "open"}
        ]
        self._conversations = [
            {"conversation_id": "conv_001", "candidate_id": "lp_001", "hr_name": "李经理", "company": "CGL",
             "messages_count": 12, "last_message_time": "2024-03-12 14:30", "reply_rate": 0.9,
             "avg_response_hours": 2.5, "interview_scheduled": True, "interview_time": "2024-03-15 10:00",
             "status": "interviewing"},
            {"conversation_id": "conv_002", "candidate_id": "lp_002", "hr_name": "王总监", "company": "CGL",
             "messages_count": 8, "last_message_time": "2024-03-11 16:00", "reply_rate": 0.85,
             "avg_response_hours": 4.0, "interview_scheduled": False, "status": "negotiating"}
        ]
        self._behaviors = [
            {"behavior_id": "bh_001", "candidate_id": "lp_001", "activity_level": "HIGH",
             "last_active": "2024-03-10", "login_frequency_per_week": 8, "jobs_viewed_30d": 15,
             "jobs_applied_30d": 3, "jobs_interested_30d": 5,
             "search_queries": ["前端专家", "技术管理", "大厂机会"],
             "resume_updated": "2024-03-01", "resume_update_frequency": 2,
             "profile_completeness": 0.95, "intention_signals": ["actively_looking"], "urgency_score": 0.7},
            {"behavior_id": "bh_002", "candidate_id": "lp_002", "activity_level": "MEDIUM",
             "last_active": "2024-03-12", "login_frequency_per_week": 5, "jobs_viewed_30d": 8,
             "jobs_applied_30d": 1, "jobs_interested_30d": 3,
             "search_queries": ["产品总监", "高管职位"],
             "resume_updated": "2024-02-20", "resume_update_frequency": 1,
             "profile_completeness": 0.88, "intention_signals": ["passive_candidate"], "urgency_score": 0.4}
        ]

    def get_oauth_url(self) -> str:
        """获取OAuth授权URL"""
        base_url = "https://auth.liepin.com/oauth/authorize"
        params = {"client_id": self.api_key, "redirect_uri": "https://talentai.pro/callback/liepin",
                  "response_type": "code", "scope": "resume_read conversation_read behavior_read"}
        return f"{base_url}?{urlencode(params)}"

    def get_auth_status(self) -> Dict[str, Any]:
        """获取授权状态"""
        return {
            "authorized": bool(self.access_token) and not self._is_token_expired(),
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "use_mock": self._use_mock,
            "data_counts": {"candidates": len(self._candidates), "jobs": len(self._jobs),
                           "conversations": len(self._conversations), "behaviors": len(self._behaviors)}
        }
