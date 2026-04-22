# -*- coding: utf-8 -*-
"""
飞书 (Feishu/Lark) 连接器 - TalentAI Pro
支持: 日历事件、文档、消息、用户数据同步
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class FeishuEventType(Enum):
    """飞书事件类型"""
    INTERVIEW = "interview"  # 面试
    ASSESSMENT = "assessment"  # 评估
    OFFER = "offer"  # offer沟通
    FEEDBACK = "feedback"  # 反馈
    NOTE = "note"  # 备注


@dataclass
class FeishuCalendarEvent:
    """飞书日历事件"""
    event_id: str
    title: str
    description: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: List[str] = field(default_factory=list)
    event_type: FeishuEventType = FeishuEventType.NOTE
    location: str = ""
    notes: str = ""


@dataclass
class FeishuDocument:
    """飞书文档"""
    doc_id: str
    title: str
    content: str = ""
    owner_id: str = ""
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


@dataclass
class FeishuMessage:
    """飞书消息"""
    message_id: str
    chat_id: str
    sender_id: str
    content: str = ""
    create_time: Optional[datetime] = None


@dataclass
class FeishuUser:
    """飞书用户"""
    user_id: str
    name: str
    email: str = ""
    phone: str = ""
    department: str = ""
    job_title: str = ""
    avatar_url: str = ""


class FeishuConnector:
    """
    飞书连接器

    功能:
    1. 日历事件同步 - 获取面试/评估日程
    2. 文档内容获取 - 获取JD/候选人信息文档
    3. 消息监听 - 获取群消息中的候选人动态
    4. 用户信息 - 获取候选人/HR联系方式

    使用方式:
    ```python
    connector = FeishuConnector(app_id="your_app_id", app_secret="your_app_secret")

    # 获取日历事件
    events = connector.get_calendar_events(start_date, end_date)

    # 获取文档
    doc = connector.get_document("doc_id")

    # 发送消息
    connector.send_message(chat_id, content)
    ```
    """

    def __init__(
        self,
        app_id: str = "",
        app_secret: str = "",
        tenant_access_token: str = ""
    ):
        """
        初始化飞书连接器

        Args:
            app_id: 飞书应用 App ID
            app_secret: 飞书应用 App Secret
            tenant_access_token: 预定义的租户访问令牌（可替代 app_id + app_secret）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = tenant_access_token
        self.base_url = "https://open.feishu.cn/open-apis"

        # Token缓存
        self._token_cache = {
            "token": "",
            "expires_at": 0
        }

        # API配置
        self._api_configs = {
            "auth": "/auth/v3/tenant_access_token/internal",
            "calendar": "/calendar/v4/calendars",
            "document": "/docx/v1/documents",
            "message": "/im/v1/messages",
            "user": "/contact/v3/users"
        }

    def _get_access_token(self) -> str:
        """
        获取访问令牌

        Returns:
            访问令牌字符串
        """
        # 检查缓存
        if self._token_cache["token"] and time.time() < self._token_cache["expires_at"]:
            return self._token_cache["token"]

        # 使用tenant_access_token
        if self.tenant_access_token:
            self._token_cache = {
                "token": self.tenant_access_token,
                "expires_at": time.time() + 7200
            }
            return self._token_cache["token"]

        # 通过app_id和app_secret获取
        if not self.app_id or not self.app_secret:
            # Mock模式
            return "mock_token"

        # TODO: 实际API调用
        # import requests
        # response = requests.post(
        #     f"{self.base_url}{self._api_configs['auth']}",
        #     json={"app_id": self.app_id, "app_secret": self.app_secret}
        # )
        # data = response.json()
        # self._token_cache = {
        #     "token": data.get("tenant_access_token", ""),
        #     "expires_at": time.time() + 7200
        # }

        return self._token_cache["token"]

    def _make_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

    # ==================== 日历相关API ====================

    def get_calendar_events(
        self,
        start_date: datetime,
        end_date: datetime,
        calendar_id: str = "primary"
    ) -> List[FeishuCalendarEvent]:
        """
        获取日历事件

        Args:
            start_date: 开始日期
            end_date: 结束日期
            calendar_id: 日历ID，默认为primary

        Returns:
            日历事件列表
        """
        # Mock数据 - 实际使用时替换为真实API调用
        if not self.app_id:
            return self._mock_calendar_events(start_date, end_date)

        # TODO: 实际API调用
        # GET /calendar/v4/calendars/{calendar_id}/events?start_time=...&end_time=...

        return self._mock_calendar_events(start_date, end_date)

    def _mock_calendar_events(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[FeishuCalendarEvent]:
        """生成Mock日历事件"""
        events = []

        # 生成2-3个mock事件
        for i in range(2):
            event_date = start_date + timedelta(days=i*2)
            events.append(FeishuCalendarEvent(
                event_id=f"evt_{i+1}",
                title=f"面试 - 候选人{i+1}" if i % 2 == 0 else f"评估 - 候选人{i+1}",
                description=f"面试评估会议 - 候选人{i+1}",
                start_time=event_date.replace(hour=10, minute=0),
                end_time=event_date.replace(hour=11, minute=0),
                attendees=[f"user_{j}" for j in range(2)],
                event_type=FeishuEventType.INTERVIEW if i % 2 == 0 else FeishuEventType.ASSESSMENT,
                location="线上视频"
            ))

        return events

    def create_calendar_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str],
        description: str = "",
        event_type: FeishuEventType = FeishuEventType.NOTE,
        calendar_id: str = "primary"
    ) -> FeishuCalendarEvent:
        """
        创建日历事件

        Args:
            title: 事件标题
            start_time: 开始时间
            end_time: 结束时间
            attendees: 参与者ID列表
            description: 事件描述
            event_type: 事件类型
            calendar_id: 日历ID

        Returns:
            创建的事件
        """
        if not self.app_id:
            # Mock模式
            return FeishuCalendarEvent(
                event_id=f"evt_{int(time.time())}",
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                attendees=attendees,
                event_type=event_type
            )

        # TODO: 实际API调用
        # POST /calendar/v4/calendars/{calendar_id}/events

        return FeishuCalendarEvent(
            event_id=f"evt_{int(time.time())}",
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            event_type=event_type
        )

    # ==================== 文档相关API ====================

    def get_document(self, doc_id: str) -> Optional[FeishuDocument]:
        """
        获取文档内容

        Args:
            doc_id: 文档ID

        Returns:
            文档对象，如果不存在返回None
        """
        if not self.app_id:
            return self._mock_document(doc_id)

        # TODO: 实际API调用
        # GET /docx/v1/documents/{doc_id}

        return self._mock_document(doc_id)

    def _mock_document(self, doc_id: str) -> FeishuDocument:
        """生成Mock文档"""
        return FeishuDocument(
            doc_id=doc_id,
            title=f"JD文档 - {doc_id}",
            content="""
# 职位描述

## 岗位职责
- 负责AI产品设计
- 带领技术团队
- 与业务部门协作

## 任职要求
- 5年以上AI产品经验
- 硕士及以上学历
- 有创业公司经验优先

## 薪资范围
- 50-80万年薪
- 期权激励
            """,
            owner_id="user_1",
            created_time=datetime.now() - timedelta(days=30),
            updated_time=datetime.now() - timedelta(days=1)
        )

    def search_documents(
        self,
        query: str,
        doc_types: List[str] = None
    ) -> List[FeishuDocument]:
        """
        搜索文档

        Args:
            query: 搜索关键词
            doc_types: 文档类型过滤

        Returns:
            匹配的文档列表
        """
        if not self.app_id:
            return [self._mock_document(f"doc_{i}") for i in range(3)]

        # TODO: 实际API调用
        # POST /docx/v1/documents/search

        return [self._mock_document(f"doc_{i}") for i in range(3)]

    # ==================== 消息相关API ====================

    def get_messages(
        self,
        chat_id: str,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 50
    ) -> List[FeishuMessage]:
        """
        获取群消息

        Args:
            chat_id: 群ID
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回消息数量限制

        Returns:
            消息列表
        """
        if not self.app_id:
            return self._mock_messages(chat_id, limit)

        # TODO: 实际API调用
        # GET /im/v1/messages?container_id_type=chat&container_id=...

        return self._mock_messages(chat_id, limit)

    def _mock_messages(self, chat_id: str, limit: int) -> List[FeishuMessage]:
        """生成Mock消息"""
        messages = []
        for i in range(min(limit, 5)):
            messages.append(FeishuMessage(
                message_id=f"msg_{i+1}",
                chat_id=chat_id,
                sender_id=f"user_{i%3}",
                content=f"群消息 {i+1} - 候选人相关讨论",
                create_time=datetime.now() - timedelta(hours=i*2)
            ))
        return messages

    def send_message(
        self,
        chat_id: str,
        content: str,
        msg_type: str = "text"
    ) -> bool:
        """
        发送消息

        Args:
            chat_id: 群ID或用户ID
            content: 消息内容
            msg_type: 消息类型

        Returns:
            是否发送成功
        """
        if not self.app_id:
            print(f"[Mock] 发送消息到 {chat_id}: {content}")
            return True

        # TODO: 实际API调用
        # POST /im/v1/messages?receive_id_type=chat_id

        return True

    # ==================== 用户相关API ====================

    def get_user(self, user_id: str) -> Optional[FeishuUser]:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            用户对象
        """
        if not self.app_id:
            return self._mock_user(user_id)

        # TODO: 实际API调用
        # GET /contact/v3/users/{user_id}?user_id_type=open_id

        return self._mock_user(user_id)

    def _mock_user(self, user_id: str) -> FeishuUser:
        """生成Mock用户"""
        return FeishuUser(
            user_id=user_id,
            name=f"用户{user_id}",
            email=f"{user_id}@company.com",
            department="人力资源部",
            job_title="招聘经理"
        )

    def get_users_by_department(
        self,
        department_id: str = "0"
    ) -> List[FeishuUser]:
        """
        获取部门下用户列表

        Args:
            department_id: 部门ID，0为根部门

        Returns:
            用户列表
        """
        if not self.app_id:
            return [self._mock_user(f"user_{i}") for i in range(5)]

        # TODO: 实际API调用
        # GET /contact/v3/users?department_id=...

        return [self._mock_user(f"user_{i}") for i in range(5)]

    # ==================== 数据转换 ====================

    def calendar_event_to_job(self, event: FeishuCalendarEvent) -> Dict[str, Any]:
        """
        将日历事件转换为Job格式

        Args:
            event: 日历事件

        Returns:
            Job格式的字典
        """
        return {
            "title": event.title.replace("面试 - ", "").replace("评估 - ", ""),
            "description": event.description,
            "requirements": [],
            "location": event.location,
            "source": "feishu",
            "source_id": event.event_id,
            "created_at": event.start_time.isoformat() if event.start_time else None
        }

    def document_to_job(self, doc: FeishuDocument) -> Dict[str, Any]:
        """
        将文档转换为Job格式

        Args:
            doc: 飞书文档

        Returns:
            Job格式的字典
        """
        return {
            "title": doc.title,
            "description": doc.content,
            "requirements": [],
            "source": "feishu",
            "source_id": doc.doc_id,
            "created_at": doc.created_time.isoformat() if doc.created_time else None,
            "updated_at": doc.updated_time.isoformat() if doc.updated_time else None
        }

    def message_to_candidate_activity(
        self,
        message: FeishuMessage
    ) -> Dict[str, Any]:
        """
        将消息转换为候选人活动

        Args:
            message: 飞书消息

        Returns:
            活动格式的字典
        """
        return {
            "type": "feishu_message",
            "content": message.content,
            "source_id": message.message_id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,
            "timestamp": message.create_time.isoformat() if message.create_time else None
        }


# ==================== 便捷函数 ====================

def create_feishu_connector(
    app_id: str = None,
    app_secret: str = None,
    tenant_access_token: str = None
) -> FeishuConnector:
    """
    创建飞书连接器的便捷函数

    Args:
        app_id: 飞书应用App ID
        app_secret: 飞书应用App Secret
        tenant_access_token: 预定义的租户访问令牌

    Returns:
        FeishuConnector实例
    """
    return FeishuConnector(
        app_id=app_id or "",
        app_secret=app_secret or "",
        tenant_access_token=tenant_access_token or ""
    )


if __name__ == "__main__":
    # 快速测试
    connector = create_feishu_connector()

    # 测试获取日历
    print("=== 测试飞书连接器 ===")
    events = connector.get_calendar_events(
        datetime.now(),
        datetime.now() + timedelta(days=7)
    )
    print(f"获取到 {len(events)} 个日历事件")
    for evt in events:
        print(f"  - {evt.title} ({evt.event_type.value})")

    # 测试获取文档
    doc = connector.get_document("test_doc_1")
    print(f"\n文档: {doc.title}")

    # 测试获取用户
    user = connector.get_user("user_1")
    print(f"\n用户: {user.name} - {user.email}")
