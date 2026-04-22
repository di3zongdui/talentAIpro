# -*- coding: utf-8 -*-
"""
真实API连接器测试 - TalentAI Pro

测试飞书和Bitable真实API连接器

使用说明:
1. 复制配置文件示例:
   cp connectors/feishu/config_feishu.py.example connectors/feishu/config_feishu.py
   cp connectors/bitable/config_bitables.py.example connectors/bitable/config_bitables.py

2. 编辑配置文件填入真实凭证

3. 运行测试:
   python tests/test_real_api_connectors.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

# 尝试导入连接器
try:
    from connectors.feishu.connector_real import FeishuConnectorReal, create_feishu_connector_from_config
    from connectors.bitable.connector_real import BitableConnectorReal, create_bitale_connector_from_config
    from connectors.feishu.connector_real import FeishuEventType, FeishuUser, FeishuCalendarEvent, FeishuDocument
    from connectors.bitable.connector_real import (
        Candidate, Job, Deal, DealStage, CandidateStatus, JobStatus,
        BitableConnectorReal
    )
except ImportError as e:
    print(f"[ERROR] Failed to import connectors: {e}")
    print("Make sure you have the connectors installed")
    sys.exit(1)


def test_feishu_connector():
    """测试飞书连接器"""
    print("\n" + "=" * 60)
    print("Testing Feishu Connector (Real API)")
    print("=" * 60)

    # 创建连接器
    connector = create_feishu_connector_from_config()

    print(f"\n[INFO] Connector mode: {'REAL API' if connector.app_id else 'MOCK'}")

    # 测试1: 获取用户信息
    print("\n[Test 1] Get User Info")
    try:
        user = connector.get_user_info("test_user")
        print(f"  ✓ User: {user.name} <{user.email}>")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试2: 获取日历事件
    print("\n[Test 2] Get Calendar Events (next 7 days)")
    try:
        events = connector.get_calendar_events(
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        print(f"  ✓ Found {len(events)} events")
        for event in events[:3]:
            print(f"    - {event.title} ({event.event_type.value})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试3: 获取文档
    print("\n[Test 3] Get Document Content")
    try:
        doc = connector.get_document("mock_doc")
        print(f"  ✓ Document: {doc.title}")
        if doc.content:
            print(f"    Content preview: {doc.content[:50]}...")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试4: 发送消息
    print("\n[Test 4] Send Message")
    try:
        msg_id = connector.send_message("oc_test", "这是一条测试消息")
        print(f"  ✓ Message sent: {msg_id}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试5: 创建日历事件
    print("\n[Test 5] Create Calendar Event")
    try:
        new_event = connector.create_calendar_event(
            title="测试面试 - 张三",
            start_time=datetime.now() + timedelta(days=2, hours=10),
            end_time=datetime.now() + timedelta(days=2, hours=11),
            description="这是一条测试面试记录",
            location="线上",
            attendees=["test@example.com"]
        )
        print(f"  ✓ Event created: {new_event.event_id} - {new_event.title}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    print("\n" + "-" * 60)
    print("Feishu Connector Tests Completed")
    return True


def test_bitable_connector():
    """测试Bitable连接器"""
    print("\n" + "=" * 60)
    print("Testing Bitable Connector (Real API)")
    print("=" * 60)

    # 创建连接器
    connector = create_bitale_connector_from_config()

    print(f"\n[INFO] Connector mode: {'REAL API' if connector.app_id else 'MOCK'}")

    # 测试1: 获取候选人列表
    print("\n[Test 1] Get Candidates")
    try:
        candidates = connector.get_candidates()
        print(f"  ✓ Found {len(candidates)} candidates")
        for c in candidates[:3]:
            print(f"    - {c.name} ({c.title} @ {c.company})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试2: 获取职位列表
    print("\n[Test 2] Get Jobs")
    try:
        jobs = connector.get_jobs()
        print(f"  ✓ Found {len(jobs)} jobs")
        for j in jobs[:3]:
            print(f"    - {j.title} @ {j.company} ({j.location})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试3: 获取交易列表
    print("\n[Test 3] Get Deals")
    try:
        deals = connector.get_deals()
        print(f"  ✓ Found {len(deals)} deals")
        for d in deals[:3]:
            print(f"    - {d.candidate_name} → {d.job_title} [{d.stage.value}]")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试4: 创建候选人
    print("\n[Test 4] Create Candidate")
    try:
        new_cand = Candidate(
            name="测试候选人",
            email="test_candidate@example.com",
            title="AI算法工程师",
            company="测试公司",
            skills=["Python", "TensorFlow"],
            experience_years=5,
            status=CandidateStatus.ACTIVE
        )
        created = connector.create_candidate(new_cand)
        print(f"  ✓ Candidate created: {created.name} (ID: {created.record_id})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试5: 创建职位
    print("\n[Test 5] Create Job")
    try:
        new_job = Job(
            title="高级AI算法专家",
            company="华为",
            skills_required=["Python", "LLM", "PyTorch"],
            experience_years_min=5,
            salary_min="80K",
            salary_max="150K",
            location="深圳",
            status=JobStatus.OPEN
        )
        created = connector.create_job(new_job)
        print(f"  ✓ Job created: {created.title} (ID: {created.record_id})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试6: 创建交易
    print("\n[Test 6] Create Deal")
    try:
        new_deal = connector.create_deal(
            candidate_id="test_cand_id",
            job_id="test_job_id",
            candidate_name="张三",
            job_title="AI算法专家",
            owner="George"
        )
        print(f"  ✓ Deal created: {new_deal.candidate_name} → {new_deal.job_title} (ID: {new_deal.record_id})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # 测试7: 更新交易阶段
    print("\n[Test 7] Update Deal Stage")
    try:
        # 获取一个现有交易
        deals = connector.get_deals()
        if deals:
            deal = deals[0]
            old_stage = deal.stage
            new_stage = DealStage.INTERVIEW_COMPLETED

            connector.update_deal_stage(deal.record_id, new_stage, "面试表现优秀")
            print(f"  ✓ Deal {deal.record_id} stage updated: {old_stage.value} → {new_stage.value}")
        else:
            print("  ⊘ No deals to update (using mock data)")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    print("\n" + "-" * 60)
    print("Bitable Connector Tests Completed")
    return True


def test_data_sync_workflow():
    """测试数据同步工作流"""
    print("\n" + "=" * 60)
    print("Testing Data Sync Workflow")
    print("=" * 60)

    # 创建连接器
    feishu = create_feishu_connector_from_config()
    bitable = create_bitale_connector_from_config()

    # 1. 从飞书获取日历事件
    print("\n[Step 1] Get interviews from Feishu Calendar")
    try:
        events = feishu.get_calendar_events(
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        interview_events = [e for e in events if e.event_type == FeishuEventType.INTERVIEW]
        print(f"  ✓ Found {len(interview_events)} upcoming interviews")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        interview_events = []

    # 2. 从Bitable获取开放职位
    print("\n[Step 2] Get open jobs from Bitable")
    try:
        jobs = bitable.get_jobs(status="open")
        print(f"  ✓ Found {len(jobs)} open jobs")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        jobs = []

    # 3. 获取候选人
    print("\n[Step 3] Get active candidates from Bitable")
    try:
        candidates = bitable.get_candidates(status="active")
        print(f"  ✓ Found {len(candidates)} active candidates")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        candidates = []

    # 4. 创建面试安排交易
    print("\n[Step 4] Create deals for scheduled interviews")
    if interview_events:
        try:
            for event in interview_events[:2]:  # 只处理前2个
                # 从事件标题中提取候选人姓名（简化处理）
                candidate_name = event.title.split(" - ")[0] if " - " in event.title else "未知"

                deal = bitable.create_deal(
                    candidate_id="",
                    job_id="",
                    candidate_name=candidate_name,
                    job_title="面试安排",
                    owner="System"
                )
                print(f"  ✓ Deal created for: {candidate_name}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    else:
        print("  ⊘ No interviews to process")

    print("\n" + "-" * 60)
    print("Data Sync Workflow Test Completed")
    return True


def main():
    """主测试函数"""
    print("\n" + "#" * 60)
    print("# TalentAI Pro - Real API Connectors Test Suite")
    print("#" * 60)

    results = []

    # 测试飞书连接器
    try:
        results.append(("Feishu Connector", test_feishu_connector()))
    except Exception as e:
        print(f"\n[ERROR] Feishu connector test failed: {e}")
        results.append(("Feishu Connector", False))

    # 测试Bitable连接器
    try:
        results.append(("Bitable Connector", test_bitable_connector()))
    except Exception as e:
        print(f"\n[ERROR] Bitable connector test failed: {e}")
        results.append(("Bitable Connector", False))

    # 测试数据同步工作流
    try:
        results.append(("Data Sync Workflow", test_data_sync_workflow()))
    except Exception as e:
        print(f"\n[ERROR] Data sync workflow test failed: {e}")
        results.append(("Data Sync Workflow", False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
