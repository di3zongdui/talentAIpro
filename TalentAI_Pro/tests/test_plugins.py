#!/usr/bin/env python
"""插件系统测试"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_plugins():
    """测试所有插件"""
    print("=" * 60)
    print("TalentAI Pro 插件系统测试")
    print("=" * 60)

    from TalentAI_Pro.plugins import (
        PluginHub,
        PluginType,
        LocalFolderPlugin,
        LiepinOAuthPlugin,
        FeishuSyncPlugin,
        FeishuNotifierPlugin,
        EmailNotifierPlugin,
        DingTalkNotifierPlugin,
        create_notification,
        Notification
    )

    # 1. 测试插件中心
    print("\n[PASS] PluginHub imported successfully")

    # 2. 测试插件注册
    hub = PluginHub()

    # 注册数据源插件
    local_plugin = LocalFolderPlugin()
    liepin_plugin = LiepinOAuthPlugin()
    feishu_plugin = FeishuSyncPlugin()

    # 注册通知插件
    feishu_notifier = FeishuNotifierPlugin()
    email_notifier = EmailNotifierPlugin()
    dingtalk_notifier = DingTalkNotifierPlugin()

    hub.register(local_plugin)
    hub.register(liepin_plugin)
    hub.register(feishu_plugin)
    hub.register(feishu_notifier)
    hub.register(email_notifier)
    hub.register(dingtalk_notifier)

    print(f"[PASS] Registered {len(hub.list_plugins())} plugins")

    # 3. 测试插件初始化
    results = {}
    for plugin in hub.list_plugins():
        success = await plugin.start()
        results[plugin.name] = success
        status = "✅" if success else "❌"
        print(f"[{status}] {plugin.name} initialized: {success}")

    # 4. 测试心跳
    print("\n--- Running Heartbeats ---")
    heartbeat_results = await hub.run_heartbeat()
    for result in heartbeat_results:
        status = "✅" if result.status.value == "success" else "❌"
        print(f"[{status}] {result.plugin_name}: +{result.items_added} items, {result.metadata}")

    # 5. 测试数据获取
    print("\n--- Fetching Data ---")
    all_data = await hub.fetch_all_data()
    print(f"[PASS] Fetched {len(all_data)} data items")

    # 按类型统计
    by_type = {}
    for item in all_data:
        if item.type not in by_type:
            by_type[item.type] = 0
        by_type[item.type] += 1

    for type_name, count in by_type.items():
        print(f"  - {type_name}: {count}")

    # 6. 测试通知
    print("\n--- Testing Notifications ---")
    notif = create_notification(
        title="测试通知",
        content="这是一条测试通知消息",
        recipients=["user1@example.com"],
        channel="feishu",
        priority="normal"
    )
    feishu_notifier.queue_notification(notif)
    print(f"[PASS] Notification queued: {notif.title}")

    # 7. 测试插件状态
    print("\n--- Plugin Status ---")
    for plugin in hub.list_plugins():
        print(f"  - {plugin.name}: {plugin.status.value}")

    # 8. 总结
    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"测试结果: {passed}/{total} 插件初始化成功")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_plugins())
    sys.exit(0 if success else 1)
