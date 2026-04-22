"""
Phase 1 测试 - 核心功能测试
"""
import sys
sys.path.insert(0, "TalentAI_Pro")

from models.job import Job, JobCreate, JobType
from models.candidate import Candidate, CandidateCreate
from engine.matching_v1 import MatchingEngineV1
from skills.jd_parser import JDParser
from skills.resume_parser import ResumeParser


def test_jd_parser():
    """测试 JD 解析器"""
    print("\n" + "=" * 60)
    print("测试 1: JD Parser")
    print("=" * 60)

    parser = JDParser()

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

    result = parser.parse(jd_text)

    print(f"\n[OK] 职位: {result.get('location')} {result.get('education_requirement')} {result.get('min_experience_years')}年+")
    print(f"[OK] 必备技能: {', '.join(result.get('required_skills', []))}")
    print(f"[OK] 隐含偏好: {len(result.get('hidden_preferences', []))}项")
    print(f"[OK] 薪资范围: {result.get('salary_range')}")

    for pref in result.get("hidden_preferences", []):
        print(f"   - {pref['keyword']}: {pref['implied_preference']}")

    return True


def test_resume_parser():
    """测试简历解析器"""
    print("\n" + "=" * 60)
    print("测试 2: Resume Parser")
    print("=" * 60)

    parser = ResumeParser()

    resume_text = """
    【李明】
    邮箱：liming@example.com
    电话：13800138000

    职位：资深算法工程师
    公司：字节跳动

    技能：Python, Java, Machine Learning, Deep Learning, NLP
    学历：硕士 - 清华大学
    经验：8年

    工作经历：
    2020-至今：字节跳动，资深算法工程师
    2016-2020：阿里巴巴，算法工程师
    """

    result = parser.parse(resume_text)

    print(f"\n[OK] 姓名: {result.get('name')}")
    print(f"[OK] 邮箱: {result.get('email')}")
    print(f"[OK] 当前职位: {result.get('current_title')}")
    print(f"[OK] 当前公司: {result.get('current_company')}")
    print(f"[OK] 技能: {', '.join(result.get('skills', []))}")
    print(f"[OK] 估算职级: {result.get('estimated_level')}")
    print(f"[OK] 教育: {result.get('education')}")

    return True


def test_matching_engine():
    """测试匹配引擎"""
    print("\n" + "=" * 60)
    print("测试 3: Matching Engine V1")
    print("=" * 60)

    # 创建职位
    job = Job(
        id="JOB-0001",
        title="具身智能HR负责人",
        company_name="某具身智能公司",
        location="北京",
        salary_min=300000,
        salary_max=500000,
        created_by="test",
        required_skills=["HR", "招聘", "人力资源管理"],
        min_experience_years=10,
        education_requirement="本科",
    )

    # 创建候选人
    candidate = Candidate(
        id="CAND-0001",
        name="Levi Li",
        location="北京",
        current_title="HR总监",
        current_company="某大厂",
        years_of_experience=12,
        expected_salary_min=1000000,
        expected_salary_max=2000000,
        preferred_locations=["北京"],
    )

    # 执行匹配
    engine = MatchingEngineV1(threshold=75.0)
    result = engine.match(job, candidate)

    print(f"\n[OK] 基础匹配分: {result.score.base_score}")
    print(f"[OK] 招聘者满意分: {result.score.recruiter_satisfaction}")
    print(f"[OK] 候选人满意分: {result.score.candidate_satisfaction}")
    print(f"[OK] 综合撮合分: {result.composite_score}")
    print(f"[OK] 技能匹配分: {result.score.skill_match_details}")
    print(f"[OK] 地点匹配分: {result.score.location_match}")
    print(f"[OK] 薪资匹配分: {result.score.salary_match}")
    print(f"[OK] 触发承诺机制: {'是' if result.commitment_triggered else '否'}")
    print(f"[OK] 推荐理由: {result.recommendation_reason}")

    return True


def test_batch_match():
    """测试批量匹配"""
    print("\n" + "=" * 60)
    print("测试 4: Batch Match")
    print("=" * 60)

    job = Job(
        id="JOB-0002",
        title="Python后端工程师",
        company_name="某科技公司",
        location="北京",
        salary_min=300000,
        salary_max=500000,
        created_by="test",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        min_experience_years=3,
    )

    candidates = [
        Candidate(
            id=f"CAND-{i:04d}",
            name=f"候选人{i}",
            location="北京",
            current_title="Python开发工程师",
            current_company="某公司",
            years_of_experience=4,
            expected_salary_min=350000,
            expected_salary_max=500000,
        )
        for i in range(5)
    ]

    engine = MatchingEngineV1(threshold=75.0)
    results = engine.batch_match(job, candidates)

    print(f"\n[OK] 批量匹配数量: {len(results)}")
    print(f"[OK] 最优匹配: {results[0].candidate_id} - {results[0].composite_score}")

    for i, r in enumerate(results[:3]):
        print(f"   Top {i+1}: {r.candidate_id} - 综合分{r.composite_score}")

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("TalentAI Pro - Phase 1 MVP 测试")
    print("=" * 60)

    tests = [
        ("JD Parser", test_jd_parser),
        ("Resume Parser", test_resume_parser),
        ("Matching Engine V1", test_matching_engine),
        ("Batch Match", test_batch_match),
    ]

    results = []
    for name, test_fn in tests:
        try:
            success = test_fn()
            results.append((name, success))
        except Exception as e:
            print(f"\n[FAIL] {name} 失败: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, success in results:
        status = "[OK] 通过" if success else "[FAIL] 失败"
        print(f"{status} - {name}")

    all_passed = all(r[1] for r in results)
    print(f"\n总体结果: {'[OK] 全部通过' if all_passed else '[FAIL] 有测试失败'}")

    return all_passed


if __name__ == "__main__":
    run_all_tests()
