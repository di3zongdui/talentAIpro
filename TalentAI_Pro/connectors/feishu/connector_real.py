# -*- coding: utf-8 -*-
"""
飞书 (Feishu/Lark) 真实API连接器 - TalentAI Pro
需要先在飞书开放平台创建应用并配置权限

创建应用流程:
1. 访问 https://open.feishu.cn/app 登录
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 配置权限:
   - calendar:readonly 日历只读
   - calendar:write 日历读写
   - docx:readonly 文档只读
   - docx:write 文档读写
   - im:readonly 消息只读
   - im:write 消息读写
   - contact:readonly 联系人只读
5. 发布应用
6. 将机器人添加到群聊

配置示例:
    cp config_feishu.py.example config_feishu.py
    # 编辑 config_feishu.py 填入真实凭证
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# 配置文件示例
# ============================================================

FEISHU_CONFIG_EXAMPLE = """
# 飞书连接器配置 - 复制此文件为 config_feishu.py 并填入真实值

# 方式1: 使用 App ID 和 App Secret（推荐）
FEISHU_APP_ID = "cli_xxxxxxxxxxxxxxxxxx"
FEISHU_APP_SECRET = "your_app_secret_here"

# 方式2: 使用预定义的 Tenant Access Token
FEISHU_TENANT_TOKEN = "t-xxxxxxxxxxxxxxxxxx"

# 日历配置
FEISHU_CALENDAR_ID = "primary"  # 使用主日历，或指定日历ID

# 默认搜索时间范围（天）
DEFAULT_SEARCH_DAYS = 30

# API重试配置
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒
"""


# ============================================================
# 枚举定义
# ============================================================

class FeishuEventType(Enum):
    """飞书事件类型枚举"""
    INTERVIEW = "interview"
    ASSESSMENT = "assessment"
    OFFER = "offer"
    FEEDBACK = "feedback"
    NOTE = "note"


# ============================================================
# 数据类定义
# ============================================================

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


# ============================================================
# 飞书连接器
# ============================================================

class FeishuConnectorReal:
    """
    飞书连接器 - 真实API版本

    支持功能:
    1. 日历事件同步 - 获取面试/评估日程
    2. 文档内容获取 - 获取JD/候选人信息文档
    3. 消息发送 - 发送通知给候选人/HR
    4. 用户信息查询 - 获取联系人详情

    使用示例:
    ```python
    # 方式1: 使用配置文件
    from config_feishu import FEISHU_APP_ID, FEISHU_APP_SECRET
    connector = FeishuConnectorReal(app_id=FEISHU_APP_ID, app_secret=FEISHU_APP_SECRET)

    # 方式2: 直接传入
    connector = FeishuConnectorReal(
        app_id="cli_xxx",
        app_secret="secret_xxx"
    )

    # 获取日历事件
    events = connector.get_calendar_events(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7)
    )

    # 发送消息
    connector.send_message(
        chat_id="oc_xxx",
        content="面试提醒: 张三 明天 14:00"
    )
    ```
    """

    def __init__(
        self,
        app_id: str = "",
        app_secret: str = "",
        tenant_access_token: str = "",
        calendar_id: str = "primary"
    ):
        """
        初始化飞书连接器

        Args:
            app_id: 飞书应用 App ID (cli_xxx)
            app_secret: 飞书应用 App Secret
            tenant_access_token: 预定义的租户访问令牌
            calendar_id: 日历ID，默认使用主日历
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = tenant_access_token
        self.calendar_id = calendar_id
        self.base_url = "https://open.feishu.cn/open-apis"

        # Token缓存
        self._token_cache = {
            "token": "",
            "expires_at": 0
        }

        # API端点配置
        self._endpoints = {
            "auth": "/auth/v3/tenant_access_token/internal",
            "calendar_list": "/calendar/v4/calendars",
            "calendar_events": "/calendar/v4/calendars/{calendar_id}/events",
            "event_detail": "/calendar/v4/calendars/{calendar_id}/events/{event_id}",
            "document": "/docx/v1/documents/{doc_id}",
            "document_blocks": "/docx/v1/documents/{doc_id}/blocks",
            "message_send": "/im/v1/messages",
            "user_info": "/contact/v3/users/{user_id}",
            "user_list": "/contact/v3/users",
        }

        # 验证配置
        self._validate_config()

    def _validate_config(self) -> None:
        """验证连接器配置"""
        if not self.tenant_access_token and (not self.app_id or not self.app_secret):
            print("[WARNING] FeishuConnector running in MOCK mode - no credentials provided")
            print("  To enable real API calls:")
            print("    1. Create app at https://open.feishu.cn/app")
            print("    2. Get App ID and App Secret")
            print("    3. Pass credentials to constructor or create config_feishu.py")

    def _get_access_token(self) -> str:
        """
        获取访问令牌

        Returns:
            访问令牌字符串

        Raises:
            Exception: API调用失败时抛出异常
        """
        # 检查缓存
        if self._token_cache["token"] and time.time() < self._token_cache["expires_at"] - 60:
            return self._token_cache["token"]

        # 使用预定义的tenant_access_token
        if self.tenant_access_token:
            self._token_cache = {
                "token": self.tenant_access_token,
                "expires_at": time.time() + 7200
            }
            return self._token_cache["token"]

        # 通过app_id和app_secret获取
        if not self.app_id or not self.app_secret:
            raise Exception("Feishu API credentials not configured")

        # 真实API调用 - 获取tenant_access_token
        url = f"{self.base_url}{self._endpoints['auth']}"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"Failed to get access token: {result.get('msg')}")

        self._token_cache = {
            "token": result.get("tenant_access_token", ""),
            "expires_at": time.time() + 7200
        }

        return self._token_cache["token"]

    def _make_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

    def _api_call(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None,
        retries: int = 3
    ) -> Dict:
        """
        通用API调用方法

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点（不含base_url）
            params: URL参数
            json_data: JSON请求体
            retries: 重试次数

        Returns:
            API响应数据

        Raises:
            Exception: API调用失败
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._make_headers()

        for attempt in range(retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=headers, json=json_data, timeout=10)
                elif method.upper() == "PUT":
                    response = requests.put(url, headers=headers, json=json_data, timeout=10)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, params=params, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                result = response.json()

                # 检查业务错误码
                if result.get("code") == 0:
                    return result.get("data", {})

                # token过期，重试
                if result.get("code") == 99991663 and attempt < retries - 1:
                    self._token_cache = {"token": "", "expires_at": 0}
                    time.sleep(1)
                    headers = self._make_headers()
                    continue

                raise Exception(f"API error: code={result.get('code')}, msg={result.get('msg')}")

            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                raise Exception(f"Request failed: {str(e)}")

        raise Exception("Max retries exceeded")

    # ==================== 日历API ====================

    def get_calendar_events(
        self,
        start_date: datetime,
        end_date: datetime,
        max_results: int = 100
    ) -> List[FeishuCalendarEvent]:
        """
        获取日历事件

        Args:
            start_date: 开始日期
            end_date: 结束日期
            max_results: 最大返回数量

        Returns:
            日历事件列表
        """
        # Mock模式
        if not self.app_id and not self.tenant_access_token:
            return self._mock_get_calendar_events(start_date, end_date)

        # 真实API调用
        endpoint = self._endpoints["calendar_events"].format(
            calendar_id=self.calendar_id
        )

        params = {
            "start_time": int(start_date.timestamp()),
            "end_time": int(end_date.timestamp()),
            "max_results": max_results
        }

        data = self._api_call("GET", endpoint, params=params)

        events = []
        for item in data.get("items", []):
            event_type = self._detect_event_type(item.get("summary", ""))

            start_ts = item.get("start_time", {})
            end_ts = item.get("end_time", {})

            events.append(FeishuCalendarEvent(
                event_id=item.get("event_id", ""),
                title=item.get("summary", ""),
                description=item.get("description", ""),
                start_time=datetime.fromtimestamp(start_ts.get("timestamp", 0)) if start_ts else None,
                end_time=datetime.fromtimestamp(end_ts.get("timestamp", 0)) if end_ts else None,
                event_type=event_type,
                location=item.get("location", {}).get("name", ""),
                attendees=[a.get("email", "") for a in item.get("attendees", [])]
            ))

        return events

    def _detect_event_type(self, title: str) -> FeishuEventType:
        """根据标题检测事件类型"""
        title_lower = title.lower()

        if any(k in title_lower for k in ["面试", "interview"]):
            return FeishuEventType.INTERVIEW
        elif any(k in title_lower for k in ["评估", "assessment"]):
            return FeishuEventType.ASSESSMENT
        elif any(k in title_lower for k in ["offer", "录用"]):
            return FeishuEventType.OFFER
        elif any(k in title_lower for k in ["反馈", "feedback"]):
            return FeishuEventType.FEEDBACK
        else:
            return FeishuEventType.NOTE

    def create_calendar_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = "",
        attendees: List[str] = None
    ) -> FeishuCalendarEvent:
        """
        创建日历事件

        Args:
            title: 事件标题
            start_time: 开始时间
            end_time: 结束时间
            description: 事件描述
            location: 地点
            attendees: 参与者邮箱列表

        Returns:
            创建的事件对象
        """
        if not self.app_id and not self.tenant_access_token:
            return self._mock_create_calendar_event(title, start_time, end_time, description)

        endpoint = self._endpoints["calendar_events"].format(
            calendar_id=self.calendar_id
        )

        payload = {
            "summary": title,
            "description": description,
            "start_time": {
                "timestamp": int(start_time.timestamp()),
                "timezone": "Asia/Shanghai"
            },
            "end_time": {
                "timestamp": int(end_time.timestamp()),
                "timezone": "Asia/Shanghai"
            },
            "location": {"name": location} if location else None,
            "attendees": [
                {"email": email, "type": "third_party"}
                for email in (attendees or [])
            ] if attendees else None
        }

        data = self._api_call("POST", endpoint, json_data=payload)

        item = data.get("event", {})
        return FeishuCalendarEvent(
            event_id=item.get("event_id", ""),
            title=item.get("summary", ""),
            description=item.get("description", ""),
            start_time=datetime.fromtimestamp(item.get("start_time", {}).get("timestamp", 0)),
            end_time=datetime.fromtimestamp(item.get("end_time", {}).get("timestamp", 0)),
            event_type=self._detect_event_type(item.get("summary", "")),
            location=item.get("location", {}).get("name", ""),
            attendees=[a.get("email", "") for a in item.get("attendees", [])]
        )

    # ==================== 文档API ====================

    def get_document(self, doc_id: str) -> FeishuDocument:
        """
        获取文档信息

        Args:
            doc_id: 文档ID

        Returns:
            文档对象
        """
        if not self.app_id and not self.tenant_access_token:
            return self._mock_get_document(doc_id)

        endpoint = self._endpoints["document"].format(doc_id=doc_id)

        data = self._api_call("GET", endpoint)

        doc = data.get("document", {})
        return FeishuDocument(
            doc_id=doc.get("document_id", ""),
            title=doc.get("title", ""),
            owner_id=doc.get("owner_id", ""),
            created_time=datetime.fromtimestamp(doc.get("create_time", 0)) if doc.get("create_time") else None,
            updated_time=datetime.fromtimestamp(doc.get("update_time", 0)) if doc.get("update_time") else None
        )

    def get_document_content(self, doc_id: str) -> str:
        """
        获取文档内容（纯文本）

        Args:
            doc_id: 文档ID

        Returns:
            文档内容（纯文本）
        """
        if not self.app_id and not self.tenant_access_token:
            doc = self._mock_get_document(doc_id)
            return doc.content

        # 获取文档块
        endpoint = self._endpoints["document_blocks"].format(doc_id=doc_id)

        all_blocks = []
        page_token = None

        while True:
            params = {"page_token": page_token} if page_token else {}
            data = self._api_call("GET", endpoint, params=params)

            items = data.get("items", [])
            all_blocks.extend(items)

            # 检查是否还有下一页
            if data.get("has_more"):
                page_token = data.get("next_page_token")
            else:
                break

        # 提取文本内容
        content = self._extract_text_from_blocks(all_blocks)
        return content

    def _extract_text_from_blocks(self, blocks: List[Dict]) -> str:
        """从文档块中提取纯文本"""
        text_parts = []

        for block in blocks:
            block_type = block.get("block_type", 0)

            # 文本块类型: 1=文本, 2=标题1, 3=标题2, 4=标题3
            if block_type in [1, 2, 3, 4]:
                text_elements = block.get("text", {}).get("elements", [])
                for element in text_elements:
                    text_run = element.get("text_run", {})
                    content_text = text_run.get("content", "")
                    if content_text:
                        text_parts.append(content_text)

            # 列表块
            elif block_type in [5, 6, 7]:  # 有序列表/无序列表/任务列表
                text_elements = block.get("text", {}).get("elements", [])
                for element in text_elements:
                    content_text = element.get("text_run", {}).get("content", "")
                    if content_text:
                        text_parts.append(f"• {content_text}")

        return "\n".join(text_parts)

    # ==================== 消息API ====================

    def send_message(
        self,
        chat_id: str,
        content: str,
        msg_type: str = "text"
    ) -> str:
        """
        发送消息

        Args:
            chat_id: 群聊ID
            content: 消息内容
            msg_type: 消息类型 (text/post/image/card)

        Returns:
            发送的消息ID
        """
        if not self.app_id and not self.tenant_access_token:
            return self._mock_send_message(chat_id, content)

        endpoint = self._endpoints["message_send"]

        payload = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps({"text": content}) if msg_type == "text" else content
        }

        data = self._api_call("POST", endpoint, json_data=payload)

        return data.get("message_id", "")

    def send_interview_reminder(
        self,
        candidate_name: str,
        interview_time: datetime,
        location: str = "",
        chat_id: str = ""
    ) -> str:
        """
        发送面试提醒

        Args:
            candidate_name: 候选人姓名
            interview_time: 面试时间
            location: 面试地点
            chat_id: 群聊ID（如果指定则发送到群，否则发送到个人）

        Returns:
            发送的消息ID
        """
        time_str = interview_time.strftime("%Y年%m月%d日 %H:%M")

        content = f"""面试提醒
候选人: {candidate_name}
时间: {time_str}
地点: {location if location else '待定'}

请提前做好准备！"""

        return self.send_message(chat_id, content)

    # ==================== 用户API ====================

    def get_user_info(self, user_id: str) -> FeishuUser:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            用户对象
        """
        if not self.app_id and not self.tenant_access_token:
            return self._mock_get_user_info(user_id)

        endpoint = self._endpoints["user_info"].format(user_id=user_id)

        params = {"user_id_type": "open_id"}

        data = self._api_call("GET", endpoint, params=params)

        user = data.get("user", {})
        return FeishuUser(
            user_id=user.get("open_id", ""),
            name=user.get("name", ""),
            email=user.get("email", ""),
            phone=user.get("mobile", ""),
            department=user.get("department", ""),
            job_title=user.get("job_title", ""),
            avatar_url=user.get("avatar", {}).get("avatar_72", "")
        )

    def get_user_by_email(self, email: str) -> Optional[FeishuUser]:
        """
        通过邮箱查询用户

        Args:
            email: 用户邮箱

        Returns:
            用户对象，如果不存在返回None
        """
        if not self.app_id and not self.tenant_access_token:
            return FeishuUser(
                user_id="mock_user",
                name="Mock User",
                email=email
            )

        params = {
            "emails": email,
            "user_id_type": "open_id"
        }

        data = self._api_call("GET", self._endpoints["user_list"], params=params)

        users = data.get("user_list", [])
        if users:
            user = users[0]
            return FeishuUser(
                user_id=user.get("open_id", ""),
                name=user.get("name", ""),
                email=user.get("email", "")
            )

        return None

    # ==================== Mock方法（测试用） ====================

    def _mock_get_calendar_events(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[FeishuCalendarEvent]:
        """Mock获取日历事件"""
        return [
            FeishuCalendarEvent(
                event_id="mock_event_001",
                title="张三 - AI算法工程师 面试",
                start_time=datetime.now() + timedelta(days=1, hours=10),
                end_time=datetime.now() + timedelta(days=1, hours=11),
                event_type=FeishuEventType.INTERVIEW,
                attendees=["zhangsan@company.com"]
            ),
            FeishuCalendarEvent(
                event_id="mock_event_002",
                title="李四 - 产品经理 评估",
                start_time=datetime.now() + timedelta(days=2, hours=14),
                end_time=datetime.now() + timedelta(days=2, hours=15),
                event_type=FeishuEventType.ASSESSMENT,
                attendees=["lisi@company.com"]
            )
        ]

    def _mock_create_calendar_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str
    ) -> FeishuCalendarEvent:
        """Mock创建日历事件"""
        return FeishuCalendarEvent(
            event_id=f"mock_event_{int(time.time())}",
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            event_type=self._detect_event_type(title)
        )

    def _mock_get_document(self, doc_id: str) -> FeishuDocument:
        """Mock获取文档"""
        return FeishuDocument(
            doc_id=doc_id,
            title=f"Mock Document {doc_id}",
            content="这是Mock文档内容。\n\n职位: AI算法工程师\n要求: Python, TensorFlow, 5年经验",
            owner_id="mock_owner"
        )

    def _mock_send_message(self, chat_id: str, content: str) -> str:
        """Mock发送消息"""
        return f"mock_message_{int(time.time())}"

    def _mock_get_user_info(self, user_id: str) -> FeishuUser:
        """Mock获取用户信息"""
        return FeishuUser(
            user_id=user_id,
            name="Mock User",
            email="mock@example.com"
        )


# ============================================================
# 便捷函数
# ============================================================

def create_feishu_connector_from_config() -> FeishuConnectorReal:
    """
    从配置文件创建飞书连接器

    Returns:
        配置好的FeishuConnectorReal实例
    """
    try:
        from config_feishu import FEISHU_APP_ID, FEISHU_APP_SECRET
        return FeishuConnectorReal(
            app_id=FEISHU_APP_ID,
            app_secret=FEISHU_APP_SECRET
        )
    except ImportError:
        print("[WARNING] config_feishu.py not found, using mock mode")
        return FeishuConnectorReal()


# ============================================================
# 入口测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Feishu Connector - Real API Test")
    print("=" * 60)

    # 尝试从配置文件加载
    connector = create_feishu_connector_from_config()

    print(f"\nConnector mode: {'REAL API' if connector.app_id else 'MOCK'}")

    # 测试获取用户信息
    print("\n[Test] Get User Info (mock)")
    user = connector.get_user_info("test_user")
    print(f"  User: {user.name} <{user.email}>")

    # 测试获取日历事件
    print("\n[Test] Get Calendar Events")
    events = connector.get_calendar_events(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7)
    )
    print(f"  Found {len(events)} events")
    for event in events:
        print(f"  - {event.title} ({event.event_type.value})")

    # 测试获取文档
    print("\n[Test] Get Document Content")
    doc = connector.get_document("mock_doc_001")
    print(f"  Title: {doc.title}")

    # 测试发送消息
    print("\n[Test] Send Message")
    msg_id = connector.send_message("oc_test", "这是一条测试消息")
    print(f"  Message ID: {msg_id}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
