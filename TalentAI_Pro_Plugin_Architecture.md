# TalentAI Pro 插件化数据更新架构

> **Version:** 1.0 | **Date:** 2026-04-23

---

## 1. 插件架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                    TalentAI Pro 插件系统                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  数据源插件   │  │  分析插件   │  │  通知插件   │            │
│   ├─────────────┤  ├─────────────┤  ├─────────────┤            │
│   │ 📁 本地文件  │  │ 🔍 背景调查 │  │ 📧 邮件通知 │            │
│   │ 📱 猎聘API  │  │ 📊 薪资预测 │  │ 💬 飞书推送 │            │
│   │ 🌐 拉勾API  │  │ ⚠️ 风险预警 │  │ 🔔 钉钉通知 │            │
│   │ 💼 领英API  │  │ 🎯 匹配优化 │  │ 📱 短信通知 │            │
│   │ 📊 Bitable │  │ 🧠 画像增强 │  │ 📱 微信推送 │            │
│   │ 📄 飞书文档 │  └─────────────┘  └─────────────┘            │
│   └─────────────┘                                               │
│          │                                                        │
│          ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                   Plugin Hub (插件中心)                   │    │
│   │   • 插件安装/卸载                                        │    │
│   │   • 插件配置                                             │    │
│   │   • 心跳调度                                             │    │
│   │   • 状态监控                                             │    │
│   └─────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                   TalentAI Core                           │    │
│   │   • JD Intelligence    • Candidate Intelligence          │    │
│   │   • Discovery Radar     • Matching Engine                 │    │
│   │   • Smart Outreach     • Deal Tracker                   │    │
│   └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 插件类型

### 2.1 数据源插件 (Source Plugins)

| 插件 | 数据类型 | 更新方式 | 优先级 |
|------|---------|---------|--------|
| **LocalFolder** | 本地简历/JD | 文件监控 | P0 |
| **FeishuSync** | 飞书文档/表格 | Webhook/API | P0 |
| **BitableSync** | 多维表格数据 | Webhook/API | P0 |
| **LiepinPlugin** | 猎聘简历/职位 | API轮询 | P1 |
| **BossPlugin** | Boss直聘数据 | Cookie+API | P1 |
| **LinkedInPlugin** | 领英人脉 | API | P1 |
| **LagouPlugin** | 拉勾职位 | API | P2 |
| **MaimaiPlugin** | 脉脉职场 | API | P2 |

### 2.2 分析插件 (Analysis Plugins)

| 插件 | 功能 | 依赖 |
|------|------|------|
| **BackgroundCheck** | 全网背景调查 | 数据源插件 |
| **SalaryPredictor** | 薪资预测 | Candidate Intelligence |
| **RiskDetector** | 风险预警 | BackgroundCheck |
| **MatchOptimizer** | 匹配算法优化 | JD+Candidate Intelligence |

### 2.3 通知插件 (Notification Plugins)

| 插件 | 渠道 | 触发条件 |
|------|------|---------|
| **EmailNotifier** | 邮件 | 新候选人/状态变更 |
| **FeishuNotifier** | 飞书消息 | 重要事件 |
| **DingTalkNotifier** | 钉钉 | 紧急告警 |
| **WeChatNotifier** | 企业微信 | 日常通知 |
| **SMSNotifier** | 短信 | 紧急联系 |

---

## 3. 插件接口定义

### 3.1 插件基类

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio

@dataclass
class PluginConfig:
    """插件配置"""
    enabled: bool = True
    heartbeat_interval: int = 300  # 秒
    retry_times: int = 3
    retry_delay: int = 60
    custom_params: Dict[str, Any] = None

@dataclass
class DataItem:
    """数据条目"""
    id: str
    source: str
    type: str  # 'candidate' | 'job'
    data: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class HeartbeatResult:
    """心跳结果"""
    success: bool
    items_added: int = 0
    items_updated: int = 0
    items_deleted: int = 0
    errors: List[str] = None

class TalentAIPlugin(ABC):
    """TalentAI 插件基类"""

    # 插件元信息
    plugin_id: str = ""
    plugin_name: str = ""
    plugin_version: str = "1.0.0"
    plugin_type: str = "source"  # source | analysis | notification
    plugin_icon: str = "🔌"
    plugin_author: str = ""
    plugin_description: str = ""

    def __init__(self, config: PluginConfig):
        self.config = config
        self.is_running = False
        self.last_heartbeat: Optional[datetime] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    @abstractmethod
    async def initialize(self) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    async def heartbeat(self) -> HeartbeatResult:
        """执行心跳，返回新增/更新/删除的数据"""
        pass

    @abstractmethod
    async def fetch_data(self, since: datetime = None) -> List[DataItem]:
        """获取数据"""
        pass

    async def start(self):
        """启动插件"""
        if not await self.initialize():
            raise RuntimeError(f"插件 {self.plugin_id} 初始化失败")

        self.is_running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.on_start()

    async def stop(self):
        """停止插件"""
        self.is_running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        await self.cleanup()
        self.on_stop()

    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.is_running:
            try:
                result = await self.heartbeat()
                self.last_heartbeat = datetime.now()
                self.on_heartbeat_success(result)
            except Exception as e:
                self.on_heartbeat_error(e)
                await asyncio.sleep(self.config.retry_delay)
            await asyncio.sleep(self.config.heartbeat_interval)

    # 钩子方法（可选重写）
    def on_start(self):
        """插件启动时调用"""
        pass

    def on_stop(self):
        """插件停止时调用"""
        pass

    def on_heartbeat_success(self, result: HeartbeatResult):
        """心跳成功时调用"""
        pass

    def on_heartbeat_error(self, error: Exception):
        """心跳失败时调用"""
        pass
```

### 3.2 数据源插件示例：本地文件夹插件

```python
import os
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class LocalFolderPlugin(TalentAIPlugin):
    """本地文件夹数据源插件"""

    plugin_id = "local_folder"
    plugin_name = "本地文件夹同步"
    plugin_type = "source"
    plugin_icon = "📁"
    plugin_description = "监控本地文件夹，自动导入简历和JD"

    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.folder_path = config.custom_params.get("folder_path", "")
        self.supported_formats = ['.pdf', '.docx', '.xlsx', '.csv', '.txt']
        self.file_states: Dict[str, str] = {}  # path -> hash

    async def initialize(self) -> bool:
        """初始化文件夹监控"""
        if not os.path.exists(self.folder_path):
            return False

        # 扫描现有文件
        await self._scan_existing_files()
        return True

    async def heartbeat(self) -> HeartbeatResult:
        """检测文件变更"""
        result = HeartbeatResult(success=True)

        current_files = self._list_files()
        current_hashes = {f: self._get_file_hash(f) for f in current_files}

        # 检测新增
        for file_path, file_hash in current_hashes.items():
            if file_path not in self.file_states:
                result.items_added += 1
                await self._process_new_file(file_path)

        # 检测更新
        for file_path, file_hash in current_hashes.items():
            if file_path in self.file_states and self.file_states[file_path] != file_hash:
                result.items_updated += 1
                await self._process_updated_file(file_path)

        # 检测删除
        for file_path in self.file_states:
            if file_path not in current_files:
                result.items_deleted += 1
                await self._process_deleted_file(file_path)

        # 更新状态
        self.file_states = current_hashes
        return result

    async def fetch_data(self, since: datetime = None) -> List[DataItem]:
        """获取文件数据"""
        items = []
        for file_path in self._list_files():
            if since and datetime.fromtimestamp(os.path.getmtime(file_path)) < since:
                continue

            item = await self._parse_file(file_path)
            if item:
                items.append(item)
        return items

    def _list_files(self) -> List[str]:
        """列出支持的文件"""
        files = []
        for root, _, filenames in os.walk(self.folder_path):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.supported_formats:
                    files.append(os.path.join(root, filename))
        return files

    def _get_file_hash(self, file_path: str) -> str:
        """获取文件hash"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    async def _process_new_file(self, file_path: str):
        """处理新文件"""
        # 触发 Group Intelligence Hub 解析
        parsed = await self.parse_file_with_ai(file_path)

        # 存储到数据库
        await self.store_to_database(parsed)

        # 触发后续分析
        await self.trigger_analysis(parsed)

    async def parse_file_with_ai(self, file_path: str) -> Dict:
        """使用AI解析文件"""
        # 调用 Group Intelligence Hub v2
        from skills.group_intelligence import GroupIntelligenceHub

        hub = GroupIntelligenceHub()
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return await hub.parse_pdf(file_path)
        elif ext == '.docx':
            return await hub.parse_docx(file_path)
        elif ext == '.xlsx':
            return await hub.parse_xlsx(file_path)
        elif ext == '.csv':
            return await hub.parse_csv(file_path)
        else:
            return await hub.parse_text(file_path)
```

### 3.3 通知插件示例：飞书通知

```python
class FeishuNotifier(TalentAIPlugin):
    """飞书通知插件"""

    plugin_id = "feishu_notifier"
    plugin_name = "飞书通知"
    plugin_type = "notification"
    plugin_icon = "💬"

    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.webhook_url = config.custom_params.get("webhook_url", "")
        self.notify_on = config.custom_params.get("notify_on", [])

    async def initialize(self) -> bool:
        """初始化飞书连接"""
        return bool(self.webhook_url)

    async def heartbeat(self) -> HeartbeatResult:
        """检查待发送通知"""
        # 检查通知队列
        pending = await self.get_pending_notifications()

        for notification in pending:
            await self.send_notification(notification)
            await self.mark_sent(notification['id'])

        return HeartbeatResult(
            success=True,
            items_added=0,
            items_updated=len(pending),
            items_deleted=0
        )

    async def fetch_data(self, since: datetime = None) -> List[DataItem]:
        return []  # 通知插件不提供数据

    async def send_notification(self, notification: Dict):
        """发送飞书消息"""
        message = self._format_feishu_message(notification)

        async with aiohttp.ClientSession() as session:
            await session.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )

    def _format_feishu_message(self, notification: Dict) -> Dict:
        """格式化飞书消息"""
        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": notification['title']},
                    "template": notification.get('level', 'blue')
                },
                "elements": [
                    {"tag": "div", "content": notification['body']},
                    {"tag": "hr"},
                    {"tag": "note", "elements": [
                        {"tag": "plain_text", "content": f"来源: TalentAI Pro | {notification['time']}"}
                    ]}
                ]
            }
        }
```

---

## 4. 插件中心 (Plugin Hub)

```python
class PluginHub:
    """TalentAI Pro 插件中心"""

    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.plugins: Dict[str, TalentAIPlugin] = {}
        self.plugin_configs: Dict[str, PluginConfig] = {}

    def register_plugin(self, plugin_class: type, config: PluginConfig):
        """注册插件"""
        plugin = plugin_class(config)
        self.plugins[plugin.plugin_id] = plugin
        self.plugin_configs[plugin.plugin_id] = config

        # 注册事件监听
        self.event_bus.subscribe(
            f"plugin.{plugin.plugin_id}.heartbeat",
            plugin.on_heartbeat
        )

    async def start_all(self):
        """启动所有插件"""
        for plugin in self.plugins.values():
            if plugin.config.enabled:
                await plugin.start()

    async def stop_all(self):
        """停止所有插件"""
        for plugin in self.plugins.values():
            await plugin.stop()

    def get_plugin_status(self) -> List[Dict]:
        """获取插件状态"""
        return [
            {
                "id": p.plugin_id,
                "name": p.plugin_name,
                "icon": p.plugin_icon,
                "type": p.plugin_type,
                "enabled": p.config.enabled,
                "running": p.is_running,
                "last_heartbeat": p.last_heartbeat.isoformat() if p.last_heartbeat else None,
                "interval": p.config.heartbeat_interval
            }
            for p in self.plugins.values()
        ]

    async def install_plugin_from_market(self, plugin_id: str) -> bool:
        """从插件市场安装插件"""
        # 调用插件市场API
        market = PluginMarket()
        plugin_info = await market.get_plugin(plugin_id)

        # 下载插件代码
        await market.download_plugin(plugin_id)

        # 安装配置
        config = PluginConfig(custom_params=plugin_info.get('default_params', {}))
        self.register_plugin_from_info(plugin_info, config)

        return True

    async def update_plugin(self, plugin_id: str):
        """更新插件"""
        # 从市场拉取最新版本
        # 重新加载插件
        pass
```

---

## 5. 插件市场

```
┌─────────────────────────────────────────────────────────────────┐
│                      插件市场                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔍 搜索插件                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  输入插件名称或功能...                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  📦 插件分类                                                     │
│  [全部] [数据源] [分析] [通知] [效率工具]                         │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                   │
│  │ 📁 本地文件夹同步  │  │ 📱 猎聘数据导入   │                   │
│  │ by TalentAI Team  │  │ by Community     │                   │
│  │ ⭐ 4.9  │ 安装    │  │ ⭐ 4.7  │ 安装    │                   │
│  └───────────────────┘  └───────────────────┘                   │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                   │
│  │ 💬 飞书通知插件   │  │ 🔍 全网背景调查   │                   │
│  │ by TalentAI Team  │  │ by Pro Member    │                   │
│  │ ⭐ 4.8  │ 安装    │  │ ⭐ 4.6  │ 安装    │                   │
│  └───────────────────┘  └───────────────────┘                   │
│                                                                 │
│  ┌───────────────────┐  ┌───────────────────┐                   │
│  │ 📊 Bitable同步    │  │ 📧 邮件通知       │                   │
│  │ by TalentAI Team  │  │ by Community     │                   │
│  │ ⭐ 4.9  │ 安装    │  │ ⭐ 4.5  │ 安装    │                   │
│  └───────────────────┘  └───────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 官方插件列表

| 插件 | 类型 | 说明 | 版本 |
|------|------|------|------|
| **LocalFolderSync** | 数据源 | 监控本地文件夹导入简历/JD | v1.0 |
| **FeishuSync** | 数据源 | 飞书文档/表格实时同步 | v1.0 |
| **BitableSync** | 数据源 | Bitable多维表格双向同步 | v1.0 |
| **LiepinConnector** | 数据源 | 猎聘简历/职位API导入 | v1.0 |
| **BossConnector** | 数据源 | Boss直聘数据采集 | v1.0 |
| **LinkedInConnector** | 数据源 | 领英人脉数据同步 | v1.0 |
| **FeishuNotifier** | 通知 | 飞书消息通知 | v1.0 |
| **EmailNotifier** | 通知 | 邮件通知 | v1.0 |
| **BackgroundCheck** | 分析 | 全网背景调查 | v1.0 |
| **SalaryPredictor** | 分析 | 薪资预测 | v1.0 |

---

## 6. 心跳协调器

```python
class HeartbeatCoordinator:
    """心跳协调器 - 协调所有插件的心跳"""

    def __init__(self, plugin_hub: PluginHub):
        self.plugin_hub = plugin_hub
        self.global_interval = 60  # 全局心跳间隔（秒）

    async def start(self):
        """启动心跳协调"""
        while True:
            start_time = datetime.now()

            # 并行执行所有插件心跳
            tasks = []
            for plugin in self.plugin_hub.plugins.values():
                if plugin.is_running:
                    tasks.append(plugin.heartbeat())

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理心跳结果
            await self._process_heartbeat_results(results)

            # 计算下一个心跳的时间
            elapsed = (datetime.now() - start_time).total_seconds()
            sleep_time = max(0, self.global_interval - elapsed)

            await asyncio.sleep(sleep_time)

    async def _process_heartbeat_results(self, results):
        """处理心跳结果"""
        total_added = 0
        total_updated = 0
        total_deleted = 0
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                total_added += result.items_added
                total_updated += result.items_updated
                total_deleted += result.items_deleted

        # 触发全局更新事件
        if total_added or total_updated or total_deleted:
            await self.event_bus.publish("data.changed", {
                "added": total_added,
                "updated": total_updated,
                "deleted": total_deleted
            })

        # 发送监控指标
        await self._report_metrics(total_added, total_updated, total_deleted, errors)
```

---

## 7. 插件配置 UI

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⚙️ 插件管理                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [📦 插件市场]  [⚙️ 已安装]  [📋 配置]  [📊 监控]                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📁 本地文件夹同步                         [开关: ●]      │   │
│  │    最后心跳: 2026-04-23 10:05:00  │  间隔: 15分钟     │   │
│  │    状态: 🟢 运行中  │  今日新增: 3  │  更新: 12        │   │
│  │    [配置] [重启] [卸载]                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 💬 飞书通知                             [开关: ●]       │   │
│  │    最后心跳: 2026-04-23 10:04:30  │  间隔: 5分钟      │   │
│  │    状态: 🟢 运行中  │  今日通知: 28                   │   │
│  │    [配置] [重启] [卸载]                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📱 猎聘数据导入                         [开关: ○]       │   │
│  │    最后心跳: -                        │  间隔: 60分钟    │   │
│  │    状态: ⚫ 已停止                                       │   │
│  │    [配置] [启用] [卸载]                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 配置: 📁 监控文件夹                                        │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ C:\Users\George Guo\Documents\简历库\              │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  │                                                      [保存] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 总结

```
┌─────────────────────────────────────────────────────────────────┐
│                      插件化架构优势                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🎯 灵活扩展 ── 按需安装/卸载插件，无需修改核心代码              │
│  🔒 隔离安全 ── 插件独立运行，单点故障不影响全局                  │
│  📦 模块复用 ── 插件可在不同项目间复用                            │
│  🚀 快速迭代 ── 插件可独立版本迭代，快速上线                      │
│  🌐 生态共建 ── 第三方可开发插件，丰富数据源                     │
│                                                                 │
│  心跳机制：                                                      │
│  • 每个插件定义自己的心跳间隔                                     │
│  • 心跳协调器统一调度，避免资源竞争                               │
│  • 心跳结果触发后续分析流程                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document Version: 1.0 | Last Updated: 2026-04-23*
