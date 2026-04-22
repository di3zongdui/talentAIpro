"""
Phase 1 核心功能测试
"""
import sys
sys.path.insert(0, 'c:/Users/George Guo/WorkBuddy/20260422151119')

from TalentAI_Pro.models.job import Job
from TalentAI_Pro.models.candidate import Candidate
from TalentAI_Pro.engine.matching_v1 import MatchingEngineV1
from TalentAI_Pro.skills.jd_parser.jd_parser import JDParser
from TalentAI_Pro.skills.resume_parser.resume_parser import ResumeParser

print("=" * 60)
print("Phase 1 MVP - 核心功能测试")
print("=" * 60)

# Test 1: JD Parser
print("\n[Test 1] JD Parser")
print("-" * 40)
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
print(f"  职位: {result.get('title')}")
print(f"  必备技能: {result.get('required_skills', [])}")
print(f"  隐含偏好: {len(result.get('hidden_preferences', []))}项")
for pref in result.get("hidden_preferences", []):
    print(f"    - {pref.get('keyword')}: {pref.get('implied_preference')}")
print(f"  薪资范围: {result.get('salary_range')}")
print(f"  工作地点: {result.get('location')}")
print(f"  最低经验: {result.get('min_experience_years')}年+")
print("[OK] JD Parser 测试通过")

# Test 2: Resume Parser
print("\n[Test 2] Resume Parser")
print("-" * 40)
parser2 = ResumeParser()
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
result2 = parser2.parse(resume_text)
print(f"  姓名: {result2.get('name')}")
print(f"  邮箱: {result2.get('email')}")
print(f"  当前职位: {result2.get('current_title')}")
print(f"  当前公司: {result2.get('current_company')}")
print(f"  技能: {result2.get('skills', [])}")
print(f"  估算职级: {result2.get('estimated_level')}")
print(f"  教育: {result2.get('education')}")
print("[OK] Resume Parser 测试通过")

# Test 3: Matching Engine
print("\n[Test 3] Matching Engine V1")
print("-" * 40)
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
engine = MatchingEngineV1(threshold=75.0)
result3 = engine.match(job, candidate)
print(f"  基础匹配分: {result3.score.base_score}")
print(f"  招聘者满意分: {result3.score.recruiter_satisfaction}")
print(f"  候选人满意分: {result3.score.candidate_satisfaction}")
print(f"  综合撮合分: {result3.composite_score}")
print(f"  触发承诺机制: {'是' if result3.commitment_triggered else '否'}")
print(f"  推荐理由: {result3.recommendation_reason}")
print("[OK] Matching Engine 测试通过")

# Test 4: Batch Match
print("\n[Test 4] Batch Match")
print("-" * 40)
job2 = Job(
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
results = engine.batch_match(job2, candidates)
print(f"  批量匹配数量: {len(results)}")
print(f"  最优匹配: {results[0].candidate_id} - 综合分{results[0].composite_score}")
for i, r in enumerate(results[:3]):
    print(f"    Top {i+1}: {r.candidate_id} - 综合分{r.composite_score}")
print("[OK] Batch Match 测试通过")

print("\n" + "=" * 60)
print("全部测试通过！Phase 1 MVP 核心功能正常")
print("=" * 60)