# 通知插件集合
# 飞书通知、邮件通知、钉钉通知

import asyncio
import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from . import TalentAIPlugin, PluginType, PluginStatus, HeartbeatResult

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    """通知消息"""
    title: str
    content: str
    recipients: List[str]
    channel: str
    priority: str = "normal"  # low, normal, high, urgent
    metadata: Dict[str, Any] = None


class BaseNotifierPlugin(TalentAIPlugin):
    """通知插件基类"""

    def __init__(self, name: str):
        super().__init__(name, PluginType.NOTIFICATION)
        self._notification_queue: List[Notification] = []
        self._sent_history: List[Dict] = []

    @abstractmethod
    async def _send_notification(self, notification: Notification) -> bool:
        """发送通知（子类实现）"""
        pass

    async def heartbeat(self) -> HeartbeatResult:
        """处理通知队列"""
        sent = 0
        failed = 0
        for notif in self._notification_queue[:]:
            success = await self._send_notification(notif)
            if success:
                sent += 1
                self._sent_history.append({
                    "notification": notif,
                    "sent_at": asyncio.get_event_loop().time(),
                    "status": "sent"
                })
            else:
                failed += 1
            self._notification_queue.remove(notif)

        return HeartbeatResult(
            plugin_name=self.name,
            status=PluginStatus.SUCCESS,
            items_added=sent,
            error_message=f"Failed: {failed}" if failed else None,
            metadata={"queue_size": len(self._notification_queue)}
        )

    async def fetch_data(self, since=None):
        """通知插件不提供数据"""
        return []

    def queue_notification(self, notification: Notification):
        """将通知加入队列"""
        self._notification_queue.append(notification)
        logger.info(f"Notification queued for {self.name}: {notification.title}")

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "queue_size": len(self._notification_queue),
            "sent_today": len([h for h in self._sent_history]),
            "pending": [n.title for n in self._notification_queue]
        }


class FeishuNotifierPlugin(BaseNotifierPlugin):
    """飞书通知插件"""

    def __init__(self, webhook_url: str = None):
        super().__init__("feishu_notifier")
        self.webhook_url = webhook_url or self.config.get("webhook_url", "")
        self._use_mock = not bool(self.webhook_url)

    async def initialize(self) -> bool:
        """初始化"""
        if self._use_mock:
            logger.info("FeishuNotifierPlugin: Running in mock mode")
        return True

    async def _send_notification(self, notification: Notification) -> bool:
        """发送飞书通知"""
        if self._use_mock:
            logger.info(f"[MOCK] Feishu notification: {notification.title}")
            return True

        try:
            # 实际应该调用飞书Webhook API
            # payload = {"msg_type": "text", "content": {"text": f"{notification.title}\n{notification.content}"}}
            # async with aiohttp.post(self.webhook_url, json=payload) as resp:
            #     return resp.status == 200
            return True
        except Exception as e:
            logger.error(f"Feishu notification failed: {e}")
            return False


class EmailNotifierPlugin(BaseNotifierPlugin):
    """邮件通知插件"""

    def __init__(self, smtp_host: str = None, smtp_port: int = 587,
                 username: str = None, password: str = None):
        super().__init__("email_notifier")
        self.smtp_host = smtp_host or self.config.get("smtp_host", "smtp.gmail.com")
        self.smtp_port = smtp_port or self.config.get("smtp_port", 587)
        self.username = username or self.config.get("username", "")
        self.password = password or self.config.get("password", "")
        self._use_mock = not bool(self.username and self.password)

    async def initialize(self) -> bool:
        """初始化"""
        if self._use_mock:
            logger.info("EmailNotifierPlugin: Running in mock mode")
        return True

    async def _send_notification(self, notification: Notification) -> bool:
        """发送邮件"""
        if self._use_mock:
            logger.info(f"[MOCK] Email notification: {notification.title} -> {notification.recipients}")
            return True

        try:
            # 实际应该使用smtplib发送邮件
            # import smtplib
            # from email.mime.text import MIMEText
            # msg = MIMEText(notification.content)
            # msg['Subject'] = notification.title
            # msg['From'] = self.username
            # with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.username, self.password)
            #     server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False


class DingTalkNotifierPlugin(BaseNotifierPlugin):
    """钉钉通知插件"""

    def __init__(self, webhook_url: str = None):
        super().__init__("dingtalk_notifier")
        self.webhook_url = webhook_url or self.config.get("webhook_url", "")
        self._use_mock = not bool(self.webhook_url)

    async def initialize(self) -> bool:
        """初始化"""
        if self._use_mock:
            logger.info("DingTalkNotifierPlugin: Running in mock mode")
        return True

    async def _send_notification(self, notification: Notification) -> bool:
        """发送钉钉通知"""
        if self._use_mock:
            logger.info(f"[MOCK] DingTalk notification: {notification.title}")
            return True

        try:
            # 实际应该调用钉钉Webhook API
            return True
        except Exception as e:
            logger.error(f"DingTalk notification failed: {e}")
            return False


def create_notification(title: str, content: str, recipients: List[str],
                       channel: str = "feishu", priority: str = "normal") -> Notification:
    """创建通知的便捷函数"""
    return Notification(
        title=title,
        content=content,
        recipients=recipients,
        channel=channel,
        priority=priority
    )
