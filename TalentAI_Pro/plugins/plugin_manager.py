# 插件管理器
# 整合所有插件，提供统一的初始化和协调

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from . import (
    PluginHub,
    PluginType,
    PluginStatus,
    TalentAIPlugin,
    LocalFolderPlugin,
    LiepinOAuthPlugin,
    FeishuSyncPlugin,
    FeishuNotifierPlugin,
    EmailNotifierPlugin,
    DingTalkNotifierPlugin,
    Notification,
    create_notification
)

logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器 - 统一管理所有插件"""

    def __init__(self):
        self.hub = PluginHub()
        self._initialized = False
        self._running = False

    def register_all_plugins(self, config: Dict[str, Any] = None):
        """注册所有插件"""
        config = config or {}

        # 数据源插件
        self.hub.register(LocalFolderPlugin(
            folder_path=config.get("local_folder_path")
        ))
        self.hub.register(LiepinOAuthPlugin(
            api_key=config.get("liepin_api_key"),
            api_secret=config.get("liepin_api_secret")
        ))
        self.hub.register(FeishuSyncPlugin(
            app_id=config.get("feishu_app_id"),
            app_secret=config.get("feishu_app_secret")
        ))

        # 通知插件
        self.hub.register(FeishuNotifierPlugin(
            webhook_url=config.get("feishu_webhook")
        ))
        self.hub.register(EmailNotifierPlugin(
            smtp_host=config.get("smtp_host"),
            smtp_port=config.get("smtp_port", 587),
            username=config.get("smtp_username"),
            password=config.get("smtp_password")
        ))
        self.hub.register(DingTalkNotifierPlugin(
            webhook_url=config.get("dingtalk_webhook")
        ))

        logger.info(f"Registered {len(self.hub.list_plugins())} plugins")

    async def initialize_all(self) -> Dict[str, bool]:
        """初始化所有插件"""
        results = {}
        for plugin in self.hub.list_plugins():
            try:
                success = await plugin.start()
                results[plugin.name] = success
            except Exception as e:
                logger.error(f"Failed to initialize {plugin.name}: {e}")
                results[plugin.name] = False
        self._initialized = True
        return results

    async def start(self):
        """启动插件系统"""
        if not self._initialized:
            await self.initialize_all()
        self._running = True
        logger.info("PluginManager started")

    async def stop(self):
        """停止插件系统"""
        for plugin in self.hub.list_plugins():
            await plugin.stop()
        self._running = False
        logger.info("PluginManager stopped")

    async def run_heartbeat_all(self) -> List:
        """运行所有插件的心跳"""
        return await self.hub.run_heartbeat()

    async def fetch_all_data(self) -> List:
        """获取所有数据"""
        return await self.hub.fetch_all_data()

    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据汇总"""
        all_data = asyncio.get_event_loop().run_until_complete(self.fetch_all_data())

        summary = {
            "total": len(all_data),
            "by_type": {},
            "by_source": {}
        }

        for item in all_data:
            # by type
            if item.type not in summary["by_type"]:
                summary["by_type"][item.type] = 0
            summary["by_type"][item.type] += 1

            # by source
            if item.source not in summary["by_source"]:
                summary["by_source"][item.source] = 0
            summary["by_source"][item.source] += 1

        return summary

    def send_notification(self, title: str, content: str, recipients: List[str],
                         channel: str = "feishu", priority: str = "normal"):
        """发送通知"""
        notif = create_notification(title, content, recipients, channel, priority)

        # 根据channel选择插件
        if channel == "feishu":
            plugin = self.hub.get_plugin("feishu_notifier")
        elif channel == "email":
            plugin = self.hub.get_plugin("email_notifier")
        elif channel == "dingtalk":
            plugin = self.hub.get_plugin("dingtalk_notifier")
        else:
            logger.warning(f"Unknown channel: {channel}")
            return

        if plugin:
            plugin.queue_notification(notif)
        else:
            logger.warning(f"Plugin for channel {channel} not found")

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        plugins = self.hub.list_plugins()
        return {
            "initialized": self._initialized,
            "running": self._running,
            "plugins": {
                "total": len(plugins),
                "by_type": {
                    "data_source": len(self.hub.list_plugins(PluginType.DATA_SOURCE)),
                    "notification": len(self.hub.list_plugins(PluginType.NOTIFICATION)),
                    "analytics": len(self.hub.list_plugins(PluginType.ANALYTICS))
                },
                "details": {p.name: {
                    "status": p.status.value,
                    "type": p.plugin_type.value,
                    "last_heartbeat": p.last_heartbeat.to_dict() if p.last_heartbeat else None
                } for p in plugins}
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.hub.to_dict()


# 全局插件管理器实例
plugin_manager = PluginManager()


# 便捷函数
async def initialize_plugins(config: Dict[str, Any] = None):
    """初始化所有插件（便捷函数）"""
    plugin_manager.register_all_plugins(config)
    return await plugin_manager.initialize_all()


async def run_plugin_heartbeat():
    """运行心跳（便捷函数）"""
    return await plugin_manager.run_heartbeat_all()


def get_plugin_data(data_type: str = None, source: str = None):
    """获取插件数据（便捷函数）"""
    if data_type:
        return plugin_manager.hub.get_data_by_type(data_type)
    elif source:
        return plugin_manager.hub.get_data_by_source(source)
    else:
        return asyncio.get_event_loop().run_until_complete(plugin_manager.fetch_all_data())
