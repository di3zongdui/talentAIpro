# -*- coding: utf-8 -*-
"""
连接器模块 - TalentAI Pro
支持飞书、Bitable等外部数据源集成
"""

from .feishu import (
    FeishuConnector,
    FeishuCalendarEvent,
    FeishuDocument,
    FeishuMessage,
    FeishuUser,
    FeishuEventType,
    create_feishu_connector
)

from .bitable import (
    BitableConnector,
    BitableApp,
    BitableTable,
    BitableField,
    BitableRecord,
    BitableFieldType,
    create_bitable_connector
)

from .sync_service import (
    DataSyncService,
    SyncConfig,
    SyncResult,
    SyncStatus,
    create_sync_service
)

__all__ = [
    # 飞书
    "FeishuConnector",
    "FeishuCalendarEvent",
    "FeishuDocument",
    "FeishuMessage",
    "FeishuUser",
    "FeishuEventType",
    "create_feishu_connector",
    # Bitable
    "BitableConnector",
    "BitableApp",
    "BitableTable",
    "BitableField",
    "BitableRecord",
    "BitableFieldType",
    "create_bitable_connector",
    # 同步服务
    "DataSyncService",
    "SyncConfig",
    "SyncResult",
    "SyncStatus",
    "create_sync_service"
]
