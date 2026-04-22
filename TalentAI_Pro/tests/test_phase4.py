# -*- coding: utf-8 -*-
"""
Phase 4 测试脚本 - 飞书/Bitable数据集成
测试飞书连接器、Bitable连接器和数据同步服务
"""

import sys
import traceback
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, "c:/Users/George Guo/WorkBuddy/20260422151119/TalentAI_Pro")

from connectors.feishu import FeishuConnector, FeishuEventType
from connectors.bitable import BitableConnector, BitableFieldType
from connectors.sync_service import DataSyncService, SyncConfig, SyncStatus


def test_feishu_connector():
    """测试飞书连接器"""
    print("\n[Test 1] Feishu Connector")

    try:
        # 创建连接器（Mock模式）
        connector = FeishuConnector()

        # 测试日历事件获取
        events = connector.get_calendar_events(
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )
        print(f"  - 获取日历事件: {len(events)} 个")
        assert len(events) > 0, "应该至少有1个日历事件"

        # 测试创建日历事件
        new_event = connector.create_calendar_event(
            title="测试面试",
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1),
            attendees=["user_1", "user_2"],
            description="AI产品总监岗位面试",
            event_type=FeishuEventType.INTERVIEW
        )
        print(f"  - 创建日历事件: {new_event.title}")

        # 测试文档获取
        doc = connector.get_document("test_doc_1")
        print(f"  - 获取文档: {doc.title}")
        assert doc.title, "文档标题不应为空"

        # 测试用户获取
        user = connector.get_user("user_1")
        print(f"  - 获取用户: {user.name} - {user.email}")
        assert user.name, "用户名不应为空"

        # 测试消息发送
        success = connector.send_message("chat_1", "测试消息")
        print(f"  - 发送消息: {'成功' if success else '失败'}")

        print("  [PASS] Feishu Connector")
        return True

    except Exception as e:
        print(f"  [FAIL] Feishu Connector: {e}")
        traceback.print_exc()
        return False


def test_bitable_connector():
    """测试Bitable连接器"""
    print("\n[Test 2] Bitable Connector")

    try:
        # 创建连接器（Mock模式）
        connector = BitableConnector()

        # 测试获取App
        app = connector.get_app()
        print(f"  - 获取App: {app.name}")
        print(f"  - 数据表数量: {len(app.tables)}")

        # 测试获取数据表
        tables = connector.get_tables()
        table_names = [t.name for t in tables]
        print(f"  - 数据表: {table_names}")
        assert "候选人库" in table_names, "应该有候选人库表"
        assert "职位库" in table_names, "应该有职位库表"

        # 测试获取候选人记录
        candidates = connector.get_records("tbl_candidates")
        print(f"  - 候选人记录: {len(candidates)}")
        assert len(candidates) > 0, "应该至少有1条候选人记录"

        # 测试记录转换
        if candidates:
            candidate = connector.record_to_candidate(candidates[0])
            print(f"  - 候选人转换: {candidate.get('name')} - {candidate.get('match_score')}")
            assert candidate.get("name"), "候选人姓名不应为空"

        # 测试获取职位记录
        jobs = connector.get_records("tbl_jobs")
        print(f"  - 职位记录: {len(jobs)}")
        assert len(jobs) > 0, "应该至少有1条职位记录"

        # 测试职位转换
        if jobs:
            job = connector.record_to_job(jobs[0])
            print(f"  - 职位转换: {job.get('title')} - {job.get('department')}")
            assert job.get("title"), "职位名称不应为空"

        # 测试创建记录
        new_record = connector.create_record("tbl_candidates", {
            "姓名": "测试候选人",
            "邮箱": "test@example.com",
            "状态": "筛选中"
        })
        print(f"  - 创建记录: {new_record.record_id}")

        print("  [PASS] Bitable Connector")
        return True

    except Exception as e:
        print(f"  [FAIL] Bitable Connector: {e}")
        traceback.print_exc()
        return False


def test_data_sync_service():
    """测试数据同步服务"""
    print("\n[Test 3] Data Sync Service")

    try:
        # 创建同步服务
        config = SyncConfig(
            bitable_app_token="test_token",
            bitable_encryption_key="test_key",
            run_jd_intelligence=True,
            run_candidate_intelligence=True,
            run_matching=True
        )
        sync_service = DataSyncService(config)

        # 测试获取同步摘要
        summary = sync_service.get_sync_summary()
        print(f"  - 同步摘要: bitable_connected={summary.get('bitable_connected')}")
        assert summary.get("bitable_connected") == True, "Bitable应该已连接"

        # 测试同步候选人
        result = sync_service.sync_candidates()
        print(f"  - 同步候选人: {result.status.value} - {result.synced_count}条")
        assert result.status == SyncStatus.SUCCESS, "同步应该成功"

        # 测试同步职位
        result = sync_service.sync_jobs()
        print(f"  - 同步职位: {result.status.value} - {result.synced_count}条")
        assert result.status == SyncStatus.SUCCESS, "同步应该成功"

        # 测试同步并匹配
        result = sync_service.sync_and_match()
        print(f"  - 同步并匹配: {result.status.value} - {result.synced_count}个匹配")
        assert result.status == SyncStatus.SUCCESS, "同步应该成功"

        # 测试生成推荐邮件
        if result.data.get("matches"):
            match = result.data["matches"][0]
            email = sync_service.generate_outreach_for_match(match)
            print(f"  - 生成推荐邮件: {len(email)}字符")
            assert len(email) > 0, "邮件内容不应为空"

        print("  [PASS] Data Sync Service")
        return True

    except Exception as e:
        print(f"  [FAIL] Data Sync Service: {e}")
        traceback.print_exc()
        return False


def test_end_to_end():
    """端到端测试：从Bitable同步到生成推荐"""
    print("\n[Test 4] End-to-End Test")

    try:
        # 创建同步服务
        sync_service = DataSyncService()

        # 1. 同步数据并匹配
        print("  - 步骤1: 同步数据并匹配")
        result = sync_service.sync_and_match()
        print(f"    结果: {result.synced_count}个匹配")

        if result.synced_count == 0:
            print("  [WARN] 没有匹配，跳过端到端测试")
            return True

        # 2. 为每个匹配生成推荐邮件
        print("  - 步骤2: 生成推荐邮件")
        for i, match in enumerate(result.data.get("matches", [])[:2]):
            email = sync_service.generate_outreach_for_match(match)
            print(f"    匹配{i+1}: {match['candidate'].get('name')} -> {match['job'].get('title')}")
            print(f"    邮件预览: {email[:100]}...")

        # 3. 从匹配创建Deal
        print("  - 步骤3: 创建Deal")
        from skills.deal_tracker.deal_tracker import DealStage
        for i, match in enumerate(result.data.get("matches", [])[:2]):
            deal = sync_service.create_deal_from_match(match, DealStage.SOURCED)
            print(f"    Deal: {deal.deal_id} - {deal.candidate_name} - {deal.stage.value}")

        # 4. 更新Deal状态
        print("  - 步骤4: 更新Deal状态")
        deals = sync_service.deal_tracker.get_all_deals()
        if deals:
            deal = deals[0]
            sync_service.deal_tracker.update_stage(deal.deal_id, DealStage.CONTACTED)
            print(f"    更新Deal {deal.deal_id} -> {DealStage.CONTACTED.value}")

        # 5. 获取漏斗统计
        print("  - 步骤5: 漏斗统计")
        stats = sync_service.deal_tracker.get_funnel_stats()
        print(f"    漏斗: {stats}")

        print("  [PASS] End-to-End Test")
        return True

    except Exception as e:
        print(f"  [FAIL] End-to-End Test: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Phase 4: 飞书/Bitable数据集成测试")
    print("=" * 60)

    results = []

    # Test 1: Feishu Connector
    results.append(("Feishu Connector", test_feishu_connector()))

    # Test 2: Bitable Connector
    results.append(("Bitable Connector", test_bitable_connector()))

    # Test 3: Data Sync Service
    results.append(("Data Sync Service", test_data_sync_service()))

    # Test 4: End-to-End
    results.append(("End-to-End Test", test_end_to_end()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Phase 4 Feishu/Bitable integration verified.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please check.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
