"""
Phase 3 Skills升级测试脚本

测试内容：
1. Smart Outreach Engine v2.0
2. Deal Tracker

运行方式：python TalentAI_Pro/tests/test_phase3.py
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from TalentAI_Pro.skills.smart_outreach.smart_outreach_engine_v2 import (
    SmartOutlookEngineV2, SurpriseHighlight, EmailVariant, CandidateStyle
)
from TalentAI_Pro.skills.deal_tracker.deal_tracker import (
    DealTracker, DealStatus, PipelineStage
)


def test_smart_outreach_engine():
    """测试 Smart Outreach Engine v2.0"""
    print("\n" + "=" * 60)
    print("[Test 1] Smart Outreach Engine v2.0")
    print("=" * 60)

    engine = SmartOutlookEngineV2()

    # 模拟超预期亮点
    candidate_highlights = [
        SurpriseHighlight(
            type="entrepreneurship",
            highlight="具身智能创业经历（与JD方向完全match）",
            source="Candidate Intelligence",
            value_level="高"
        ),
        SurpriseHighlight(
            type="management",
            highlight="管理50人团队（超出JD要求）",
            source="Resume解析",
            value_level="高"
        ),
        SurpriseHighlight(
            type="background",
            highlight="大厂P9背景",
            source="Discovery Radar",
            value_level="中"
        )
    ]

    job_highlights = [
        "2026年Q1融资200亿，赛道最热方向",
        "创始团队来自斯坦福/清华"
    ]

    # 测试1：生成完整邮件
    print("\n--- 生成完整邮件 ---")
    email = engine.generate_email(
        candidate_name="Levi Li",
        candidate_title="HR总监",
        company_name="某具身智能创业公司",
        job_title="具身智能HR负责人",
        job_highlights=job_highlights,
        candidate_highlights=candidate_highlights,
        variant=EmailVariant.COMPLETE
    )

    print(f"  主题：{email.subject}")
    print(f"  变体：{email.variant.value}")
    print(f"  使用的亮点数：{len(email.surprise_highlights_used)}")

    assert email.subject, "邮件主题不应为空"
    assert email.body, "邮件正文不应为空"
    assert len(email.surprise_highlights_used) > 0, "应包含超预期亮点"

    print("  [PASS] 生成完整邮件")

    # 测试2：生成3种变体
    print("\n--- 生成3种变体 ---")
    variants = engine.generate_variants(
        candidate_name="Levi Li",
        candidate_title="HR总监",
        company_name="某具身智能创业公司",
        job_title="具身智能HR负责人",
        job_highlights=job_highlights,
        candidate_highlights=candidate_highlights
    )

    assert len(variants) == 3, "应生成3种变体"
    print(f"  生成变体数：{len(variants)}")

    variant_names = [v.variant.value for v in variants]
    print(f"  变体类型：{variant_names}")
    print("  [PASS] 生成3种变体")

    # 测试3：跟进时机建议
    print("\n--- 跟进时机建议 ---")
    timing = engine.get_followup_timing(candidate_linkedin_active=True)
    print(f"  最佳日期：{timing['best_days']}")
    print(f"  建议：{timing['followup_suggestion']}")

    assert len(timing['best_days']) > 0, "应有最佳日期"
    assert timing['followup_suggestion'], "应有跟进建议"
    print("  [PASS] 跟进时机建议")

    # 测试4：拒绝话术
    print("\n--- 拒绝话术 ---")
    rejection = engine.get_rejection_message("salary_mismatch", "张三", keep_connection=True)
    print(f"  拒绝话术预览：{rejection[:50]}...")

    assert "张三" in rejection, "应包含候选人姓名"
    assert len(rejection) > 50, "拒绝话术应有实质内容"
    print("  [PASS] 拒绝话术")

    print("\n[PASS] Smart Outreach Engine v2.0 测试通过!")
    return True


def test_deal_tracker():
    """测试 Deal Tracker"""
    print("\n" + "=" * 60)
    print("[Test 2] Deal Tracker")
    print("=" * 60)

    tracker = DealTracker()

    # 测试1：创建Deal
    print("\n--- 创建Deal ---")
    deal = tracker.create_deal(
        candidate_id="CAND-001",
        candidate_name="Levi Li",
        candidate_title="HR总监",
        job_id="JOB-001",
        job_title="具身智能HR负责人",
        client_name="某具身智能公司",
        match_score=85.0,
        composite_score=78.0,
        surprise_highlights=["具身智能创业经验", "管理50人团队"],
        consultant="George"
    )

    print(f"  Deal ID：{deal.deal_id}")
    print(f"  候选人：{deal.candidate_name}")
    print(f"  状态：{deal.current_status.value}")
    print(f"  撮合分：{deal.composite_score}")

    assert deal.deal_id, "Deal ID不应为空"
    assert deal.current_status == DealStatus.CANDIDATE_VIEWING, "初始状态应为CANDIDATE_VIEWING"
    print("  [PASS] 创建Deal")

    # 测试2：状态更新
    print("\n--- 状态更新 ---")
    tracker.update_status(deal.deal_id, DealStatus.CANDIDATE_INTERESTED, note="候选人回复有兴趣")
    print(f"  新状态：{deal.current_status.value}")

    assert deal.current_status == DealStatus.CANDIDATE_INTERESTED, "状态应更新为CANDIDATE_INTERESTED"
    print("  [PASS] 状态更新")

    # 测试3：追踪邮件打开
    print("\n--- 追踪邮件打开 ---")
    tracker.track_email_opened(deal.deal_id)
    tracker.track_email_opened(deal.deal_id)  # 再次打开
    print(f"  打开次数：{deal.open_count}")
    print(f"  邮件打开标记：{deal.email_opened}")

    assert deal.open_count == 2, "打开次数应为2"
    assert deal.email_opened == True, "应有邮件打开标记"
    print("  [PASS] 追踪邮件打开")

    # 测试4：追踪邮件回复
    print("\n--- 追踪邮件回复 ---")
    tracker.track_email_replied(deal.deal_id)
    print(f"  邮件回复标记：{deal.email_replied}")
    print(f"  当前状态：{deal.current_status.value}")

    assert deal.email_replied == True, "应有邮件回复标记"
    assert deal.current_status == DealStatus.CANDIDATE_INTERESTED, "状态应保持CANDIDATE_INTERESTED"
    print("  [PASS] 追踪邮件回复")

    # 测试5：添加备注
    print("\n--- 添加备注 ---")
    tracker.add_note(deal.deal_id, "与候选人进行了30分钟电话沟通，反馈积极")
    print(f"  事件数：{len(deal.events)}")

    assert len(deal.events) > 0, "应有事件记录"
    print("  [PASS] 添加备注")

    # 测试6：创建跟进提醒
    print("\n--- 创建跟进提醒 ---")
    from datetime import datetime, timedelta
    reminder = tracker.create_reminder(
        deal_id=deal.deal_id,
        reminder_type="follow_up",
        scheduled_at=datetime.now() + timedelta(hours=2),
        message="候选人已回复，建议24小时内安排面试"
    )
    print(f"  提醒ID：{reminder.reminder_id}")
    print(f"  提醒类型：{reminder.reminder_type}")

    assert reminder, "应创建提醒"
    print("  [PASS] 创建跟进提醒")

    # 测试7：Deal摘要
    print("\n--- Deal摘要 ---")
    summary = tracker.get_deal_summary(deal.deal_id)
    print(f"  Deal ID：{summary['deal_id']}")
    print(f"  当前状态：{summary['current_status']}")
    print(f"  下一步行动：{summary['next_action']}")

    assert summary['deal_id'] == deal.deal_id, "摘要Deal ID应匹配"
    print("  [PASS] Deal摘要")

    # 测试8：漏斗统计
    print("\n--- 漏斗统计 ---")
    stats = tracker.get_pipeline_stats()
    print(f"  总Deal数：{stats['total_deals']}")
    print(f"  阶段分布：{stats['stage_distribution']}")

    assert stats['total_deals'] > 0, "应有Deal统计"
    print("  [PASS] 漏斗统计")

    print("\n[PASS] Deal Tracker 测试通过!")
    return True


def test_end_to_end():
    """端到端测试：Skills闭环"""
    print("\n" + "=" * 60)
    print("[Test 3] 端到端测试：Skills闭环")
    print("=" * 60)

    # 模拟完整流程
    print("\n--- Step 1: 创建Deal ---")
    tracker = DealTracker()
    deal = tracker.create_deal(
        candidate_id="CAND-E2E-001",
        candidate_name="Celina Zhang",
        candidate_title="嵌入式工程师",
        job_id="JOB-E2E-001",
        job_title="具身智能嵌入式工程师",
        client_name="某具身智能公司",
        match_score=82.0,
        composite_score=75.0,
        surprise_highlights=["大疆系背景", "具身智能创业经验"],
        consultant="George"
    )
    print(f"  Deal创建成功：{deal.deal_id}")

    print("\n--- Step 2: 生成触达邮件 ---")
    outreach = SmartOutlookEngineV2()
    highlights = [SurpriseHighlight(
        type="background",
        highlight="大疆系背景（中国硬科技黄埔军校）",
        source="Discovery Radar",
        value_level="高"
    )]
    job_hl = ["2026年Q1具身智能融资200亿", "小米+红杉联合投资"]
    email = outreach.generate_email(
        candidate_name="Celina Zhang",
        candidate_title="嵌入式工程师",
        company_name="某科技公司",
        job_title="具身智能嵌入式工程师",
        job_highlights=job_hl,
        candidate_highlights=highlights
    )
    print(f"  邮件主题：{email.subject}")
    print(f"  超预期亮点注入：{len(email.surprise_highlights_used)}项")

    print("\n--- Step 3: 追踪邮件状态 ---")
    tracker.track_email_opened(deal.deal_id)
    tracker.track_email_replied(deal.deal_id)
    tracker.update_status(deal.deal_id, DealStatus.CANDIDATE_INTERVIEWING, note="候选人确认参加面试")
    print(f"  邮件打开：{deal.email_opened}")
    print(f"  邮件回复：{deal.email_replied}")
    print(f"  当前状态：{deal.current_status.value}")

    print("\n--- Step 4: 漏斗统计 ---")
    stats = tracker.get_pipeline_stats()
    print(f"  总Deal：{stats['total_deals']}")
    print(f"  面试中：{stats['stage_distribution'].get('面试', 0)}")

    print("\n[PASS] 端到端测试完成!")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 35)
    print("TalentAI Pro - Phase 3 Skills Tests")
    print("=" * 35)

    tests = [
        ("Smart Outreach Engine v2.0", test_smart_outreach_engine),
        ("Deal Tracker", test_deal_tracker),
        ("End-to-End Test", test_end_to_end),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "[PASS]", success))
        except Exception as e:
            print(f"\n[FAIL] {name} test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, f"[FAIL]: {e}", False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, status, _ in results if status.startswith("[PASS]"))
    total = len(results)

    for name, status, _ in results:
        print(f"  {status} - {name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Phase 3 Skills verified.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please check.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)