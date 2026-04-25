"""
Channel Integrations - 渠道集成模块
====================================
支持微信、邮件、短信等渠道的消息发送

Usage:
    from skills.negotiation.channel_integrations import ChannelIntegration, WeChatChannel, EmailChannel

    # 发送微信消息
    wechat = WeChatChannel()
    result = await wechat.send_message(
        to_user="candidate_001",
        content="您收到一个新的Offer..."
    )

    # 发送邮件
    email = EmailChannel()
    result = await email.send_message(
        to="candidate@example.com",
        subject="您的Offer已更新",
        body="..."
    )
"""

import os
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import json


class ChannelType(str, Enum):
    """渠道类型"""
    WECHAT = "wechat"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"
    FAILED = "failed"


@dataclass
class ChannelMessage:
    """渠道消息"""
    id: str
    channel: ChannelType
    to: str  # 收件人标识
    subject: Optional[str]  # 邮件主题
    body: str  # 消息内容
    status: MessageStatus = MessageStatus.PENDING
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    read_at: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.sent_at is None:
            self.sent_at = datetime.now().isoformat()


class ChannelIntegration(ABC):
    """渠道集成抽象基类"""

    def __init__(self):
        self.channel_type: ChannelType = ChannelType.IN_APP

    @abstractmethod
    async def send_message(
        self,
        to: str,
        body: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """发送消息"""
        pass

    @abstractmethod
    async def get_message_status(self, message_id: str) -> MessageStatus:
        """获取消息状态"""
        pass

    async def send_negotiation_message(
        self,
        to: str,
        negotiation_content: Dict[str, Any],
        channel_specific_params: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """
        发送谈判专用消息（模板化处理）

        Args:
            to: 收件人
            negotiation_content: 谈判内容（包含offer、proposals等）
            channel_specific_params: 渠道特定参数
        """
        # 根据渠道类型格式化消息
        formatted = self._format_negotiation_message(negotiation_content)
        return await self.send_message(
            to=to,
            body=formatted["body"],
            subject=formatted.get("subject"),
            metadata=negotiation_content,
        )

    def _format_negotiation_message(
        self,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """格式化谈判消息为渠道适配的格式"""
        # 子类可以重写此方法
        return {
            "body": content.get("message", str(content)),
            "subject": None,
        }


class WeChatChannel(ChannelIntegration):
    """微信渠道"""

    def __init__(self):
        super().__init__()
        self.channel_type = ChannelType.WECHAT
        self._app_id = os.getenv("WECHAT_APP_ID", "")
        self._app_secret = os.getenv("WECHAT_APP_SECRET", "")
        self._template_id = os.getenv("WECHAT_NEGOTIATION_TEMPLATE_ID", "")

        # 模拟消息存储（生产环境应连接微信服务器）
        self._sent_messages: Dict[str, ChannelMessage] = {}

    async def send_message(
        self,
        to: str,
        body: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """发送微信消息"""
        import uuid
        msg_id = f"wechat_{uuid.uuid4().hex[:12]}"

        message = ChannelMessage(
            id=msg_id,
            channel=self.channel_type,
            to=to,
            subject=None,
            body=body,
            status=MessageStatus.PENDING,
            metadata=metadata or {},
        )

        # 模拟发送（实际应调用微信API）
        success = await self._send_to_wechat_api(message)

        if success:
            message.status = MessageStatus.SENT
            message.sent_at = datetime.now().isoformat()
        else:
            message.status = MessageStatus.FAILED

        self._sent_messages[msg_id] = message
        return message

    async def _send_to_wechat_api(self, message: ChannelMessage) -> bool:
        """
        调用微信API发送消息

        生产环境实现：
        1. 获取Access Token
        2. 调用发送模板消息或客服消息API
        3. 处理返回值
        """
        # 模拟API调用
        await asyncio.sleep(0.1)  # 模拟网络延迟

        # 检查是否配置了真实API凭证
        if not self._app_id or not self._app_secret:
            print(f"[WeChat] Mock send to {message.to}: {message.body[:50]}...")
            return True

        # 实际API调用（伪代码）
        # url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        # payload = {
        #     "touser": message.to,
        #     "template_id": self._template_id,
        #     "data": {...}
        # }
        # response = await httpx.post(url, json=payload)

        return True

    async def get_message_status(self, message_id: str) -> MessageStatus:
        """获取微信消息状态"""
        if message_id in self._sent_messages:
            return self._sent_messages[message_id].status
        return MessageStatus.FAILED

    async def send_negotiation_update(
        self,
        to_user: str,
        candidate_name: str,
        offer_summary: Dict[str, Any],
        next_action: str,
    ) -> ChannelMessage:
        """发送谈判状态更新（使用模板）"""
        body = self._build_negotiation_template(
            candidate_name=candidate_name,
            offer_summary=offer_summary,
            next_action=next_action,
        )

        return await self.send_message(
            to=to_user,
            body=body,
            metadata={
                "type": "negotiation_update",
                "candidate_name": candidate_name,
            },
        )

    def _build_negotiation_template(
        self,
        candidate_name: str,
        offer_summary: Dict[str, Any],
        next_action: str,
    ) -> str:
        """构建微信谈判通知模板"""
        salary = offer_summary.get("salary", 0)
        signing_bonus = offer_summary.get("signing_bonus", 0)

        return f"""{candidate_name}，您好！

您的Offer谈判有新进展：

💰 月薪：¥{salary:,}
🎁 签字费：¥{signing_bonus:,}

{next_action}

— TalentAI Pro
"""

    def _format_negotiation_message(
        self,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """格式化谈判消息为微信格式"""
        proposals = content.get("proposals", [])
        message = content.get("message", {})

        if isinstance(message, dict):
            body = message.get("body", str(content))
        else:
            body = str(message)

        # 微信消息限制，通常需要简洁
        if len(body) > 500:
            body = body[:500] + "..."

        return {
            "body": body,
            "subject": None,
        }


class EmailChannel(ChannelIntegration):
    """邮件渠道"""

    def __init__(self):
        super().__init__()
        self.channel_type = ChannelType.EMAIL
        self._smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self._smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self._smtp_user = os.getenv("SMTP_USER", "")
        self._smtp_password = os.getenv("SMTP_PASSWORD", "")
        self._from_email = os.getenv("FROM_EMAIL", "noreply@talentai.pro")

        # 模拟消息存储
        self._sent_messages: Dict[str, ChannelMessage] = {}

    async def send_message(
        self,
        to: str,
        body: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """发送邮件"""
        import uuid
        msg_id = f"email_{uuid.uuid4().hex[:12]}"

        if subject is None:
            subject = "TalentAI Pro - Offer 谈判更新"

        message = ChannelMessage(
            id=msg_id,
            channel=self.channel_type,
            to=to,
            subject=subject,
            body=body,
            status=MessageStatus.PENDING,
            metadata=metadata or {},
        )

        # 模拟发送（实际应连接SMTP服务器）
        success = await self._send_via_smtp(message)

        if success:
            message.status = MessageStatus.SENT
            message.sent_at = datetime.now().isoformat()
        else:
            message.status = MessageStatus.FAILED

        self._sent_messages[msg_id] = message
        return message

    async def _send_via_smtp(self, message: ChannelMessage) -> bool:
        """
        通过SMTP发送邮件

        生产环境实现：
        1. 连接SMTP服务器
        2. 认证
        3. 发送邮件
        """
        # 模拟API调用
        await asyncio.sleep(0.1)

        # 检查是否配置了真实SMTP凭证
        if not self._smtp_user or not self._smtp_password:
            print(f"[Email] Mock send to {message.to}: {message.subject}")
            return True

        # 实际SMTP发送（伪代码）
        # import smtplib
        # from email.mime.text import MIMEText
        #
        # msg = MIMEText(message.body, 'html')
        # msg['Subject'] = message.subject
        # msg['From'] = self._from_email
        # msg['To'] = message.to
        #
        # with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
        #     server.starttls()
        #     server.login(self._smtp_user, self._smtp_password)
        #     server.send_message(msg)

        return True

    async def get_message_status(self, message_id: str) -> MessageStatus:
        """获取邮件状态"""
        if message_id in self._sent_messages:
            return self._sent_messages[message_id].status
        return MessageStatus.FAILED

    def _format_negotiation_message(
        self,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """格式化谈判消息为邮件格式"""
        proposals = content.get("proposals", [])
        message = content.get("message", {})

        if isinstance(message, dict):
            subject = message.get("subject", "Offer 谈判更新")
            body = message.get("body", str(content))
        else:
            subject = "Offer 谈判更新"
            body = str(message)

        return {
            "body": self._build_html_email(body, content),
            "subject": subject,
        }

    def _build_html_email(self, body: str, content: Dict[str, Any]) -> str:
        """构建HTML邮件"""
        proposals_html = ""
        proposals = content.get("proposals", [])
        if proposals:
            proposals_html = """
            <h3>💼 方案选项</h3>
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr style="background: #f5f5f5;">
                    <th style="padding: 10px; border: 1px solid #ddd;">方案</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">月薪</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">签字费</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">推荐</th>
                </tr>
            """
            for p in proposals[:3]:  # 最多显示3个方案
                components = p.get("components", {})
                recommended = "✅" if p.get("recommended") else ""
                proposals_html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{p.get('title', '')}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">¥{components.get('salary', 0):,}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">¥{components.get('signing_bonus', 0):,}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{recommended}</td>
                </tr>
                """
            proposals_html += "</table>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏢 TalentAI Pro</h1>
                    <p>Offer 谈判更新</p>
                </div>
                <div class="content">
                    {body}
                    {proposals_html}
                </div>
                <div class="footer">
                    <p>此邮件由 TalentAI Pro 自动发送</p>
                    <p>© 2026 TalentAI Pro. 保留所有权利。</p>
                </div>
            </div>
        </body>
        </html>
        """


class SMSChannel(ChannelIntegration):
    """短信渠道"""

    def __init__(self):
        super().__init__()
        self.channel_type = ChannelType.SMS
        self._api_key = os.getenv("SMS_API_KEY", "")
        self._api_url = os.getenv("SMS_API_URL", "")

        # 模拟消息存储
        self._sent_messages: Dict[str, ChannelMessage] = {}

    async def send_message(
        self,
        to: str,
        body: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """发送短信"""
        import uuid
        msg_id = f"sms_{uuid.uuid4().hex[:12]}"

        # 短信长度限制
        if len(body) > 200:
            body = body[:197] + "..."

        message = ChannelMessage(
            id=msg_id,
            channel=self.channel_type,
            to=to,
            subject=None,
            body=body,
            status=MessageStatus.PENDING,
            metadata=metadata or {},
        )

        success = await self._send_via_api(message)

        if success:
            message.status = MessageStatus.SENT
            message.sent_at = datetime.now().isoformat()
        else:
            message.status = MessageStatus.FAILED

        self._sent_messages[msg_id] = message
        return message

    async def _send_via_api(self, message: ChannelMessage) -> bool:
        """通过短信API发送"""
        await asyncio.sleep(0.1)

        if not self._api_key:
            print(f"[SMS] Mock send to {message.to}: {message.body[:50]}...")
            return True

        # 实际API调用（伪代码）
        # response = await httpx.post(
        #     self._api_url,
        #     headers={"Authorization": f"Bearer {self._api_key}"},
        #     json={"to": message.to, "message": message.body}
        # )
        return True

    async def get_message_status(self, message_id: str) -> MessageStatus:
        """获取短信状态"""
        if message_id in self._sent_messages:
            return self._sent_messages[message_id].status
        return MessageStatus.FAILED


class ChannelRouter:
    """渠道路由器 - 根据配置选择合适的渠道发送消息"""

    def __init__(self):
        self._channels: Dict[ChannelType, ChannelIntegration] = {
            ChannelType.WECHAT: WeChatChannel(),
            ChannelType.EMAIL: EmailChannel(),
            ChannelType.SMS: SMSChannel(),
            ChannelType.IN_APP: InAppChannel(),
        }

    def get_channel(self, channel_type: ChannelType) -> ChannelIntegration:
        """获取指定渠道"""
        return self._channels.get(channel_type, self._channels[ChannelType.IN_APP])

    async def send_via_channel(
        self,
        channel_type: ChannelType,
        to: str,
        body: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """通过指定渠道发送"""
        channel = self.get_channel(channel_type)
        return await channel.send_message(to, body, subject, metadata)

    async def send_negotiation_auto(
        self,
        contact_info: Dict[str, str],
        negotiation_content: Dict[str, Any],
        preferred_channel: ChannelType = ChannelType.WECHAT,
    ) -> ChannelMessage:
        """
        自动选择最佳渠道发送谈判消息

        Args:
            contact_info: 联系信息（包含email, wechat, phone等）
            negotiation_content: 谈判内容
            preferred_channel: 首选渠道
        """
        # 根据联系信息选择渠道
        if preferred_channel == ChannelType.WECHAT and "wechat" in contact_info:
            to = contact_info["wechat"]
        elif preferred_channel == ChannelType.EMAIL and "email" in contact_info:
            to = contact_info["email"]
        elif preferred_channel == ChannelType.SMS and "phone" in contact_info:
            to = contact_info["phone"]
        elif "email" in contact_info:
            to = contact_info["email"]
            preferred_channel = ChannelType.EMAIL
        elif "wechat" in contact_info:
            to = contact_info["wechat"]
            preferred_channel = ChannelType.WECHAT
        else:
            raise ValueError("No valid contact information provided")

        channel = self.get_channel(preferred_channel)
        return await channel.send_negotiation_message(to, negotiation_content)


class InAppChannel(ChannelIntegration):
    """应用内通知渠道"""

    def __init__(self):
        super().__init__()
        self.channel_type = ChannelType.IN_APP
        self._notifications: Dict[str, List[ChannelMessage]] = {}

    async def send_message(
        self,
        to: str,
        body: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChannelMessage:
        """发送应用内通知"""
        import uuid
        msg_id = f"inapp_{uuid.uuid4().hex[:12]}"

        message = ChannelMessage(
            id=msg_id,
            channel=self.channel_type,
            to=to,
            subject=subject,
            body=body,
            status=MessageStatus.DELIVERED,  # 应用内消息直接送达
            metadata=metadata or {},
        )
        message.delivered_at = datetime.now().isoformat()
        message.sent_at = datetime.now().isoformat()

        # 存储通知
        if to not in self._notifications:
            self._notifications[to] = []
        self._notifications[to].append(message)

        return message

    async def get_message_status(self, message_id: str) -> MessageStatus:
        return MessageStatus.READ  # 应用内消息默认已读

    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[ChannelMessage]:
        """获取用户通知"""
        notifications = self._notifications.get(user_id, [])
        if unread_only:
            notifications = [n for n in notifications if n.status != MessageStatus.READ]
        return notifications


# 全局渠道路由器
_channel_router: Optional[ChannelRouter] = None


def get_channel_router() -> ChannelRouter:
    """获取全局渠道路由器"""
    global _channel_router
    if _channel_router is None:
        _channel_router = ChannelRouter()
    return _channel_router
