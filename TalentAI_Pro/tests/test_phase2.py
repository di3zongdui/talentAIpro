"""
Phase 2 Skills升级测试脚本

测试内容：
1. JD Intelligence Engine v2.0
2. Candidate Intelligence Engine v2.0
3. Discovery Radar
4. Matching Engine v2

运行方式：python TalentAI_Pro/tests/test_phase2.py
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from TalentAI_Pro.skills.jd_parser.jd_intelligence_v2 import JDIntelligenceEngineV2, JDSurpriseHighlight
from TalentAI_Pro.skills.resume_parser.candidate_intelligence_v2 import CandidateIntelligenceEngineV2
from TalentAI_Pro.skills.discovery_radar.discovery_radar import DiscoveryRadar
from TalentAI_Pro.engine.matching_v2 import MatchingEngineV2
from TalentAI_Pro.models.job import Job
from TalentAI_Pro.models.candidate import Candidate


def test_jd_intelligence_v2():
    """测试 JD Intelligence Engine v2.0"""
    print("\n" + "=" * 60)
    print("[Test 1] JD Intelligence Engine v2.0")
    print("=" * 60)

    engine = JDIntelligenceEngineV2()

    jd_text = """
    招聘：具身智能HR负责人
    公司：某具身智能创业公司

    要求：
    - 985本科及以上学历
    - 10年以上HR经验
    - 有从0到1搭建招聘体系经验
    - 有AI/技术人才招聘经验优先
    - 有创业心态

    薪资：30-50万/年
    地点：北京
    """

    report = engine.analyze(jd_text, job_type="HR")

    print(f"\n✓ 职位分析完成：{report.title}")
    print(f"  - 隐含偏好挖掘：{len(report.hidden_preferences)}项")
    for pref in report.hidden_preferences[:3]:
        print(f"    → {pref['keyword']}: {pref['implied_preference'][:30]}...")

    print(f"  - 候选人稀缺性：{'⭐' * report.scarcity.scarcity_level}（{report.scarcity.estimated_pool_size}）")
    print(f"  - 薪资竞争力：{report.salary_competitiveness.competitiveness_score}/100")
    print(f"  - 匹配难度：{report.matching_difficulty.value}")
    print(f"  - JD吸引力评分：{report.attractiveness_score}/100")

    assert report.hidden_preferences is not None, "隐含偏好挖掘失败"
    assert len(report.hidden_preferences) >= 2, "应识别出至少2项隐含偏好"
    assert report.scarcity.scarcity_level >= 3, "应识别出较稀缺人才"
    assert report.salary_competitiveness is not None, "薪资校准失败"

    print("\n✅ JD Intelligence Engine v2.0 测试通过！")
    return True


def test_candidate_intelligence_v2():
    """测试 Candidate Intelligence Engine v2.0"""
    print("\n" + "=" * 60)
    print("[Test 2] Candidate Intelligence Engine v2.0")
    print("=" * 60)

    engine = CandidateIntelligenceEngineV2()

    resume_text = """
    【Levi Li】

    邮箱：levi.li@example.com
    电话：13900001111
    地点：北京

    当前职位：HR总监
    当前公司：某具身智能创业公司（创业中）

    工作经历：
    2024-至今：具身智能创业，HR负责人
    2020-2024：某大厂，HR总监（P9级），管理50人团队
    2015-2020：某互联网公司，HR经理
    2012-2015：某咨询公司，HR专员

    教育背景：
    硕士 - 清华大学
    本科 - 985高校

    技能：
    人力资源管理、招聘体系搭建、组织发展、绩效管理
    GitHub开源项目经历
    """

    report = engine.analyze(resume_text)

    print(f"\n✓ 候选人分析完成：{report.name}")
    print(f"  - 估算职级：{report.estimated_level}")
    print(f"  - 超预期亮点：{len(report.surprise_highlights)}项")
    for h in report.surprise_highlights[:3]:
        print(f"    → [{h.type}] {h.highlight} ({h.value_level})")

    print(f"  - 风险预警：{len(report.risk_warnings)}项")
    for w in report.risk_warnings:
        print(f"    ⚠️ {w.severity.value}: {w.description[:30]}...")

    if report.salary_prediction:
        print(f"  - 薪资预测：{report.salary_prediction.estimated_min/10000:.0f}-{report.salary_prediction.estimated_max/10000:.0f}万")

    print(f"  - 文化契合度：{report.culture_fit_score}/100")
    print(f"  - 综合评级：{report.overall_rating}")

    assert report.surprise_highlights is not None, "超预期亮点发现失败"
    assert len(report.surprise_highlights) >= 2, "应识别出至少2项亮点"
    assert report.estimated_level is not None, "职级估算失败"
    assert report.overall_rating in ["A", "B", "C", "D"], "综合评级失败"

    print("\n✅ Candidate Intelligence Engine v2.0 测试通过！")
    return True


def test_discovery_radar():
    """测试 Discovery Radar"""
    print("\n" + "=" * 60)
    print("[Test 3] Discovery Radar")
    print("=" * 60)

    # 模拟搜索函数
    def mock_search(query):
        results = []
        if "具身智能" in query or "机器人" in query:
            results.append({
                "snippet": "自变量机器人完成近20亿元B轮融资，小米战投+红杉中国联合领投",
                "url": "https://example.com/news"
            })
        elif "GitHub" in query or "github" in query.lower():
            results.append({
                "snippet": "GitHub star 500+，开源项目活跃",
                "url": "https://github.com/example"
            })
        elif "融资" in query:
            results.append({
                "snippet": "2026年Q1具身智能赛道融资200亿元，同比+60%",
                "url": "https://example.com/funding"
            })
        return results

    radar = DiscoveryRadar(search_func=mock_search)

    # 测试候选人调查
    print("\n--- 候选人背景调查 ---")
    candidate_report = radar.investigate_candidate(
        name="Levi Li",
        company="某具身智能公司",
        title="HR总监"
    )
    print(f"✓ 候选人：{candidate_report.name}")
    print(f"  - 超预期亮点：{len(candidate_report.overall_surprise_highlights)}项")
    for h in candidate_report.overall_surprise_highlights[:2]:
        print(f"    → {h['highlight']}")
    print(f"  - 招聘建议：{candidate_report.hiring_recommendation}")

    # 测试公司调查
    print("\n--- 公司背景调查 ---")
    company_report = radar.investigate_company(
        company_name="自变量机器人",
        industry="具身智能"
    )
    print(f"✓ 公司：{company_report.company_name}")
    print(f"  - 超预期亮点：{len(company_report.overall_surprise_highlights)}项")
    for h in company_report.overall_surprise_highlights[:2]:
        print(f"    → {h['highlight']}")
    if company_report.risk_alerts:
        print(f"  - 风险预警：{company_report.risk_alerts[0]}")

    assert candidate_report.overall_surprise_highlights is not None, "候选人亮点发现失败"
    assert company_report.overall_surprise_highlights is not None, "公司亮点发现失败"

    print("\n✅ Discovery Radar 测试通过！")
    return True


def test_matching_engine_v2():
    """测试 Matching Engine v2"""
    print("\n" + "=" * 60)
    print("[Test 4] Matching Engine v2 (双向匹配 + 超预期惊喜分)")
    print("=" * 60)

    engine = MatchingEngineV2(threshold=75.0)

    job = Job(
        id="JOB-2026-001",
        title="具身智能HR负责人",
        company_name="某具身智能公司",
        location="北京",
        salary_min=300000,
        salary_max=500000,
        created_by="test",
        required_skills=["HR", "招聘", "人力资源管理", "组织发展"],
        preferred_skills=["AI人才招聘", "从0到1搭建"],
        min_experience_years=10,
    )

    candidate = Candidate(
        id="CAND-2026-001",
        name="Levi Li",
        location="北京",
        current_title="HR总监",
        current_company="某大厂",
        years_of_experience=12,
        expected_salary_min=1000000,
        expected_salary_max=2000000,
        preferred_locations=["北京"],
    )

    # 直接使用pydantic模型的格式创建候选人智能报告
    from skills.resume_parser.candidate_intelligence_v2 import SurpriseHighlight

    # 创建一个符合匹配引擎期望的候选人智能报告
    class CandidateIntelWrapper:
        """包装器，适配matching_v2的期望"""
        def __init__(self):
            self.surprise_highlights = [
                SurpriseHighlight(
                    type="entrepreneurship",
                    highlight="具身智能创业经历（与JD方向完全match）",
                    evidence="2024-至今创业",
                    value_level="高"
                ),
                SurpriseHighlight(
                    type="management",
                    highlight="管理50人团队（超出JD要求）",
                    evidence="HR总监管50人",
                    value_level="高"
                ),
                SurpriseHighlight(
                    type="background",
                    highlight="大厂P9背景",
                    evidence="知名大厂HR总监",
                    value_level="中"
                ),
            ]
            self.risk_warnings = []
            self.estimated_level = "D"

    candidate_intel = CandidateIntelWrapper()

    result = engine.match(
        job, candidate,
        candidate_intelligence=candidate_intel
    )

    print(f"\n✓ 匹配完成：{result.job_id} × {result.candidate_id}")
    print(f"  - 基础匹配分：{result.score.base_score}")
    print(f"  - 超预期惊喜分：{result.score.surprise_score}")
    print(f"  - 最终综合分：{result.composite_score}")
    print(f"  - 招聘者满意分：{result.score.recruiter_satisfaction}")
    print(f"  - 候选人满意分：{result.score.candidate_satisfaction}")
    print(f"  - 触发承诺机制：{'✅ 是' if result.commitment_triggered else '❌ 否'}")
    print(f"  - 推荐理由：{result.recommendation_reason}")

    assert result.score is not None, "评分计算失败"
    assert result.score.surprise_score > 0, "超预期惊喜分应为正"
    assert result.composite_score > 0, "综合撮合分应大于0"

    # 验证v2新特性
    print("\n--- v2 新特性验证 ---")
    print(f"  ✅ 超预期惊喜分已计算：{result.score.surprise_score}")
    print(f"  ✅ 双向满意分已计算：招聘者{result.score.recruiter_satisfaction} / 候选人{result.score.candidate_satisfaction}")

    print("\n✅ Matching Engine v2 测试通过！")
    return True


def test_end_to_end():
    """端到端测试：JD → 候选人 → 匹配"""
    print("\n" + "=" * 60)
    print("[Test 5] 端到端测试：JD Intelligence + Candidate + Matching")
    print("=" * 60)

    # 1. 分析JD
    jd_engine = JDIntelligenceEngineV2()
    jd_text = """
    招聘：具身智能HR负责人
    公司：某具身智能创业公司
    要求：
    - 985本科及以上
    - 10年以上HR经验
    - 有从0到1搭建招聘体系经验
    - 有AI/技术人才招聘经验
    - 有创业心态
    薪资：30-50万/年
    地点：北京
    """
    jd_report = jd_engine.analyze(jd_text, job_type="HR")
    print(f"\n[Step 1] JD分析完成")
    print(f"  - 识别{len(jd_report.hidden_preferences)}项隐含偏好")
    print(f"  - 稀缺性：{'⭐' * jd_report.scarcity.scarcity_level}")
    print(f"  - 匹配难度：{jd_report.matching_difficulty.value}")

    # 2. 分析候选人
    cand_engine = CandidateIntelligenceEngineV2()
    resume_text = """
    【Levi Li】
    当前职位：HR总监
    当前公司：某具身智能创业公司
    工作经历：12年HR经验，管理50人团队
    教育背景：硕士 - 清华大学
    技能：人力资源管理、招聘体系搭建、组织发展
    """
    cand_report = cand_engine.analyze(resume_text)
    print(f"\n[Step 2] 候选人分析完成")
    print(f"  - 职级估算：{cand_report.estimated_level}")
    print(f"  - 超预期亮点：{len(cand_report.surprise_highlights)}项")
    print(f"  - 综合评级：{cand_report.overall_rating}")

    # 3. 转换为模型
    job = Job(
        id="JOB-E2E-001",
        title=jd_report.title,
        company_name="某具身智能公司",
        location=jd_report.location,
        salary_min=jd_report.salary_range.get("min", 300000),
        salary_max=jd_report.salary_range.get("max", 500000),
        created_by="e2e_test",
        required_skills=["HR", "招聘", "人力资源管理"],
        min_experience_years=10,
    )

    candidate = Candidate(
        id="CAND-E2E-001",
        name=cand_report.name,
        location=cand_report.location,
        current_title=cand_report.current_title,
        current_company=cand_report.current_company,
        years_of_experience=cand_report.years_of_experience,
        preferred_locations=[cand_report.location] if cand_report.location else ["北京"],
    )

    # 4. 匹配
    match_engine = MatchingEngineV2(threshold=75.0)

    # 添加一个超预期亮点
    from skills.resume_parser.candidate_intelligence_v2 import SurpriseHighlight
    cand_report.surprise_highlights.append(
        SurpriseHighlight(
            type="entrepreneurship",
            highlight="具身智能创业经验（与JD完全match）",
            evidence="2024-至今",
            value_level="高"
        )
    )

    result = match_engine.match(job, candidate, candidate_intelligence=cand_report)

    print(f"\n[Step 3] 匹配完成")
    print(f"  - 综合撮合分：{result.composite_score}")
    print(f"  - 触发阈值：{match_engine.threshold}")
    print(f"  - 推荐：{result.recommendation_reason[:50]}...")

    print("\n[PASS] End-to-end test completed!")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 35)
    print("TalentAI Pro - Phase 2 Skills Upgrade Tests")
    print("=" * 35)

    tests = [
        ("JD Intelligence Engine v2.0", test_jd_intelligence_v2),
        ("Candidate Intelligence Engine v2.0", test_candidate_intelligence_v2),
        ("Discovery Radar", test_discovery_radar),
        ("Matching Engine v2", test_matching_engine_v2),
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
        print("\n[SUCCESS] All tests passed! Phase 2 Skills upgrade verified.")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please check.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)