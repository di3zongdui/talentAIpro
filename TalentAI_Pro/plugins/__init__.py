# TalentAI Pro Plugin System
# 插件系统基类和数据模型

from . import (
    TalentAIPlugin,
    PluginType,
    PluginStatus,
    HeartbeatResult,
    DataItem,
    PluginHub,
    plugin_hub
)

# 数据源插件
from .local_folder_plugin import LocalFolderPlugin
from .liepin_oauth_plugin import LiepinOAuthPlugin
from .feishu_sync_plugin import FeishuSyncPlugin

# 通知插件
from .notification_plugins import (
    FeishuNotifierPlugin,
    EmailNotifierPlugin,
    DingTalkNotifierPlugin,
    create_notification,
    Notification
)

__all__ = [
    # 核心
    "TalentAIPlugin",
    "PluginType",
    "PluginStatus",
    "HeartbeatResult",
    "DataItem",
    "PluginHub",
    "plugin_hub",
    # 数据源插件
    "LocalFolderPlugin",
    "LiepinOAuthPlugin",
    "FeishuSyncPlugin",
    # 通知插件
    "FeishuNotifierPlugin",
    "EmailNotifierPlugin",
    "DingTalkNotifierPlugin",
    "create_notification",
    "Notification",
]
