"""
Matching Engine v2 - 双向匹配 + 超预期惊喜分

功能升级：
1. 双向匹配（招聘者满意 × 候选人满意）
2. 超预期惊喜分注入
3. 撮合阈值动态调整
"""
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import math
import uuid
from datetime import datetime

from ..models.job import Job
from ..models.candidate import Candidate
from ..models.match import MatchResult, MatchScore, MatchConfidence


class MatchingEngineV2:
    """
    匹配引擎 v2 - 超预期双向匹配

    在v1基础上增加：
    1. 超预期惊喜分（recruiter_surprise + candidate_surprise）
    2. 动态阈值调整
    3. 匹配理由生成（带超预期亮点）
    """

    def __init__(self, threshold: float = 75.0):
        """
        初始化匹配引擎

        Args:
            threshold: 基础触发阈值，默认75分
        """
        self.threshold = threshold

        # 惊喜分权重
        self.SURPRISE_WEIGHTS = {
            "recruiter_surprise": 0.15,  # 候选人超预期亮点权重
            "candidate_surprise": 0.10,   # 公司超预期亮点权重
        }

        # 超预期亮点类型
        self.RECRUITER_SURPRISE_TYPES = [
            "github", "paper", "entrepreneurship",
            "management", "education", "background"
        ]
        self.CANDIDATE_SURPRISE_TYPES = [
            "funding", "team", "technology", "market_position"
        ]

    def match(
        self,
        job: Job,
        candidate: Candidate,
        jd_intelligence: Any = None,
        candidate_intelligence: Any = None,
        company_radar_report=None,
        candidate_radar_report=None,
    ) -> MatchResult:
        """
        执行双向匹配（带超预期惊喜分）

        Args:
            job: 职位对象
            candidate: 候选人对象
            jd_intelligence: JD智能分析报告（可选）
            candidate_intelligence: 候选人智能分析报告（可选）
            company_radar_report: 公司雷达报告（可选）
            candidate_radar_report: 候选人雷达报告（可选）

        Returns:
            MatchResult: 匹配结果
        """
        # 1. 计算基础匹配分
        skill_match = self._calculate_skill_match(job, candidate)
        experience_match = self._calculate_experience_match(job, candidate)
        location_match = self._calculate_location_match(job, candidate)
        salary_match = self._calculate_salary_match(job, candidate)

        base_score = (
            skill_match * 0.4 +
            experience_match * 0.3 +
            location_match * 0.15 +
            salary_match * 0.15
        )

        # 2. 计算招聘者满意分
        recruiter_satisfaction = self._calculate_recruiter_satisfaction(
            job, candidate, skill_match, experience_match
        )

        # 3. 计算候选人满意分
        candidate_satisfaction = self._calculate_candidate_satisfaction(
            job, candidate, location_match, salary_match
        )

        # 4. 计算超预期惊喜分
        recruiter_surprise = self._calculate_recruiter_surprise(
            candidate, candidate_intelligence, candidate_radar_report
        )
        candidate_surprise = self._calculate_candidate_surprise(
            job, jd_intelligence, company_radar_report
        )

        # 5. 计算最终综合分
        # v2公式：基础分 + 招聘者惊喜分 + 候选人惊喜分
        final_score = (
            base_score * (1 - self.SURPRISE_WEIGHTS["recruiter_surprise"] - self.SURPRISE_WEIGHTS["candidate_surprise"]) +
            recruiter_surprise * self.SURPRISE_WEIGHTS["recruiter_surprise"] +
            candidate_surprise * self.SURPRISE_WEIGHTS["candidate_surprise"]
        )

        # 综合撮合分（双向满意 × √惊喜分）
        # 惊喜分越高，撮合分放大效应越明显
        combined_satisfaction = recruiter_satisfaction * math.sqrt(candidate_satisfaction / 100)
        surprise_boost = 1 + (recruiter_surprise + candidate_surprise) / 200  # 惊喜分加成
        composite_score = combined_satisfaction * surprise_boost

        # 6. 构建评分对象
        score = MatchScore(
            base_score=round(base_score, 2),
            surprise_score=round(recruiter_surprise + candidate_surprise, 2),
            final_score=round(final_score, 2),
            recruiter_satisfaction=round(recruiter_satisfaction, 2),
            candidate_satisfaction=round(candidate_satisfaction, 2),
            skill_match_details={"skill_match": round(skill_match, 2)},
            experience_match=round(experience_match, 2),
            location_match=round(location_match, 2),
            salary_match=round(salary_match, 2),
            confidence=self._get_confidence(skill_match, experience_match, recruiter_surprise),
        )

        # 7. 判断触发条件
        commitment_triggered = composite_score >= self.threshold

        # 8. 构建匹配结果
        # 7. 构建匹配结果（适配pydantic模型）
        candidate_highlights = []
        if candidate_intelligence and hasattr(candidate_intelligence, 'surprise_highlights'):
            for h in candidate_intelligence.surprise_highlights:
                if hasattr(h, 'highlight'):
                    candidate_highlights.append({
                        "type": getattr(h, 'type', 'unknown'),
                        "highlight": h.highlight,
                        "value_level": getattr(h, 'value_level', '中')
                    })

        company_highlights = []
        if company_radar_report and hasattr(company_radar_report, 'overall_surprise_highlights'):
            company_highlights = company_radar_report.overall_surprise_highlights

        risk_warnings_list = []
        if candidate_intelligence and hasattr(candidate_intelligence, 'risk_warnings'):
            for w in candidate_intelligence.risk_warnings:
                if hasattr(w, 'description'):
                    risk_warnings_list.append(w.description)

        result = MatchResult(
            id=f"MATCH-{uuid.uuid4().hex[:8].upper()}",
            job_id=job.id,
            candidate_id=candidate.id,
            score=score,
            candidate_surprise_highlights=candidate_highlights,
            company_surprise_highlights=company_highlights,
            commitment_triggered=commitment_triggered,
            recruiter_threshold_met=recruiter_satisfaction >= self.threshold,
            candidate_threshold_met=candidate_satisfaction >= self.threshold,
            composite_score=round(composite_score, 2),
            risk_warnings=risk_warnings_list,
            recommendation_reason=self._generate_recommendation_v2(
                job, candidate, base_score, composite_score,
                recruiter_surprise, candidate_surprise,
                candidate_intelligence, jd_intelligence
            )
        )

        return result

    def batch_match(
        self,
        job: Job,
        candidates: List[Candidate],
        candidate_intelligences: Optional[Dict[str, Any]] = None,
        candidate_radar_reports: Optional[Dict[str, Any]] = None,
    ) -> List[MatchResult]:
        """
        批量匹配

        Args:
            job: 职位对象
            candidates: 候选人列表
            candidate_intelligences: 候选人智能报告字典 {candidate_id: report}
            candidate_radar_reports: 候选人雷达报告字典

        Returns:
            List[MatchResult]: 匹配结果列表，按综合撮合分降序排列
        """
        results = []
        for candidate in candidates:
            ci = candidate_intelligences.get(candidate.id) if candidate_intelligences else None
            cr = candidate_radar_reports.get(candidate.id) if candidate_radar_reports else None
            match_result = self.match(
                job, candidate,
                candidate_intelligence=ci,
                candidate_radar_report=cr
            )
            results.append(match_result)

        # 按综合撮合分降序排列
        results.sort(key=lambda x: x.composite_score, reverse=True)
        return results

    def _calculate_recruiter_surprise(
        self,
        candidate: Candidate,
        candidate_intelligence: Any = None,
        candidate_radar_report=None
    ) -> float:
        """
        计算招聘者惊喜分

        候选人有哪些超出JD要求的东西，让招聘者惊喜
        """
        surprise_score = 0.0
        surprise_details = []

        # 1. 从候选人智能报告获取亮点
        if candidate_intelligence:
            for highlight in candidate_intelligence.surprise_highlights:
                if highlight.type in self.RECRUITER_SURPRISE_TYPES:
                    if highlight.value_level == "高":
                        surprise_score += 15
                        surprise_details.append(f"{highlight.highlight}(高)")
                    elif highlight.value_level == "中":
                        surprise_score += 8
                        surprise_details.append(f"{highlight.highlight}(中)")

        # 2. 稀缺性加成
        if candidate_intelligence:
            if candidate_intelligence.estimated_level in ["VP", "D+", "P9"]:
                surprise_score += 10
                surprise_details.append("高级别人才")

        # 3. 跨行业/跨赛道加成
        # 如：候选人从竞品来，带来了行业知识
        # 这个需要外部数据注入，暂时标记

        return min(surprise_score, 30.0)  # 上限30分

    def _calculate_candidate_surprise(
        self,
        job: Job,
        jd_intelligence: Any = None,
        company_radar_report=None
    ) -> float:
        """
        计算候选人惊喜分

        JD/公司有哪些超出候选人期望的东西，让候选人惊喜
        """
        surprise_score = 0.0
        surprise_details = []

        # 1. 从JD智能报告获取亮点
        if jd_intelligence:
            for highlight in jd_intelligence.surprise_highlights:
                if highlight.value_level == "高":
                    surprise_score += 10
                    surprise_details.append(f"{highlight.highlight}(高)")

        # 2. 公司融资/估值加成
        if company_radar_report:
            # 如果公司刚完成大额融资，对候选人来说是惊喜
            highlights = company_radar_report.overall_surprise_highlights
            for h in highlights:
                if h.get("type") == "funding":
                    surprise_score += 10
                    surprise_details.append("公司融资顺利")

        # 3. 成长空间加成
        if jd_intelligence:
            if any("从0搭建" in pref.get("keyword", "") for pref in jd_intelligence.hidden_preferences):
                surprise_score += 8
                surprise_details.append("从0搭建机会")

        return min(surprise_score, 25.0)  # 上限25分

    def _generate_recommendation_v2(
        self,
        job: Job,
        candidate: Candidate,
        base_score: float,
        composite_score: float,
        recruiter_surprise: float,
        candidate_surprise: float,
        candidate_intelligence: Any = None,
        jd_intelligence: Any = None,
    ) -> str:
        """生成带超预期亮点的推荐理由"""
        reasons = []

        # 基础评价
        if composite_score >= 80:
            reasons.append(f"强力推荐：综合撮合分{composite_score:.1f}，超过触发阈值{self.threshold}")
        elif composite_score >= 65:
            reasons.append(f"建议尝试：综合撮合分{composite_score:.1f}")

        # 招聘者惊喜
        if recruiter_surprise >= 15:
            if candidate_intelligence:
                top_highlights = [
                    h.highlight for h in candidate_intelligence.surprise_highlights[:2]
                ]
                if top_highlights:
                    reasons.append(f"候选人有超预期亮点：{top_highlights[0]}")
        elif recruiter_surprise >= 8:
            reasons.append("候选人背景有亮点")

        # 候选人惊喜
        if candidate_surprise >= 10:
            reasons.append("JD/公司对候选人有吸引力")

        # 风险提示
        if candidate_intelligence and candidate_intelligence.risk_warnings:
            warnings = candidate_intelligence.risk_warnings[:1]
            reasons.append(f"⚠️ {warnings[0].description}")

        return "；".join(reasons) if reasons else f"综合撮合分{composite_score:.1f}"

    # 以下方法从v1继承，保持不变
    def _calculate_skill_match(self, job: Job, candidate: Candidate) -> float:
        """计算技能匹配分"""
        if not job.required_skills:
            return 80.0

        candidate_skills = self._extract_candidate_skills(candidate)
        if not candidate_skills:
            return 30.0

        matched = sum(1 for skill in job.required_skills
                     if any(skill.lower() in cs.lower() or cs.lower() in skill.lower()
                            for cs in candidate_skills))

        if job.preferred_skills:
            preferred_matched = sum(1 for skill in job.preferred_skills
                                    if any(skill.lower() in cs.lower() or cs.lower() in skill.lower()
                                           for cs in candidate_skills))
            preferred_score = (preferred_matched / len(job.preferred_skills)) * 100 if job.preferred_skills else 0
        else:
            preferred_score = 0

        required_score = (matched / len(job.required_skills)) * 100 if job.required_skills else 0
        return required_score * 0.7 + preferred_score * 0.3

    def _extract_candidate_skills(self, candidate: Candidate) -> List[str]:
        """从候选人画像提取技能列表"""
        skills = []
        if candidate.current_title:
            skills.append(candidate.current_title)
        if candidate.github_data and "skills" in candidate.github_data:
            skills.extend(candidate.github_data["skills"])
        if candidate.linkedin_data and "skills" in candidate.linkedin_data:
            skills.extend(candidate.linkedin_data["skills"])
        return list(set(skills))

    def _calculate_experience_match(self, job: Job, candidate: Candidate) -> float:
        """计算经验匹配分"""
        if not job.min_experience_years:
            return 80.0

        candidate_years = getattr(candidate, "years_of_experience", 0)

        if candidate_years >= job.min_experience_years:
            excess = candidate_years - job.min_experience_years
            if excess <= 2:
                return 90.0
            elif excess <= 5:
                return 80.0
            else:
                return 70.0
        else:
            deficit = job.min_experience_years - candidate_years
            return max(0, 80 - deficit * 10)

    def _calculate_location_match(self, job: Job, candidate: Candidate) -> float:
        """计算地点匹配分"""
        if not job.location:
            return 80.0

        candidate_locations = candidate.preferred_locations or []
        if not candidate_locations:
            if candidate.location:
                candidate_locations = [candidate.location]
            else:
                return 70.0

        for loc in candidate_locations:
            if job.location in loc or loc in job.location:
                return 100.0

        if self._same_city(job.location, candidate_locations):
            return 80.0

        return 40.0

    def _same_city(self, job_location: str, candidate_locations: List[str]) -> bool:
        """判断是否同一城市"""
        job_city = job_location.split()[0] if job_location else ""
        for loc in candidate_locations:
            if job_city in loc or loc in job_city:
                return True
        return False

    def _calculate_salary_match(self, job: Job, candidate: Candidate) -> float:
        """计算薪资匹配分"""
        if not job.salary_min or not job.salary_max:
            return 70.0

        candidate_expected_min = candidate.expected_salary_min or 0
        candidate_expected_max = candidate.expected_salary_max or 999999

        if candidate_expected_max < job.salary_min:
            return 30.0
        elif candidate_expected_min > job.salary_max:
            return 50.0
        else:
            overlap_min = max(job.salary_min, candidate_expected_min)
            overlap_max = min(job.salary_max, candidate_expected_max)
            overlap_ratio = (overlap_max - overlap_min) / (job.salary_max - job.salary_min) if job.salary_max != job.salary_min else 1
            return 60 + overlap_ratio * 40

    def _calculate_recruiter_satisfaction(
        self, job: Job, candidate: Candidate, skill_match: float, experience_match: float
    ) -> float:
        """计算招聘者满意分"""
        return skill_match * 0.6 + experience_match * 0.4

    def _calculate_candidate_satisfaction(
        self, job: Job, candidate: Candidate, location_match: float, salary_match: float
    ) -> float:
        """计算候选人满意分"""
        return location_match * 0.3 + salary_match * 0.7

    def _get_confidence(
        self, skill_match: float, experience_match: float, surprise_score: float = 0
    ) -> MatchConfidence:
        """获取匹配置信度"""
        avg = (skill_match + experience_match) / 2
        if surprise_score >= 15:
            return MatchConfidence.HIGH  # 有惊喜分，提高置信度
        elif avg >= 80:
            return MatchConfidence.HIGH
        elif avg >= 60:
            return MatchConfidence.MEDIUM
        else:
            return MatchConfidence.LOW


def demo():
    """演示Matching Engine v2"""
    from ..models.job import Job
    from ..models.candidate import Candidate

    engine = MatchingEngineV2(threshold=75.0)

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

    # 模拟候选人智能报告（有超预期亮点）
    from ..skills.resume_parser.candidate_intelligence_v2 import (
        CandidateIntelligenceReport, SurpriseHighlight
    )

    candidate_intel = CandidateIntelligenceReport(
        name="Levi Li",
        current_title="HR总监",
        current_company="某大厂",
        years_of_experience=12,
        location="北京",
        surprise_highlights=[
            SurpriseHighlight(
                type="entrepreneurship",
                highlight="具身智能创业经历",
                evidence="2024-至今创业",
                value_level="高"
            ),
            SurpriseHighlight(
                type="management",
                highlight="管理50人团队",
                evidence="HR总监管50人",
                value_level="高"
            ),
        ],
        risk_warnings=[],
        salary_prediction=None,
        job_intention=None,
        estimated_level="D",
        culture_fit_score=85.0,
        culture_fit_analysis="稳定性好，大厂背景",
        overall_rating="A",
        rating_reasons=["高级别人才", "稀缺性强"]
    )

    result = engine.match(
        job, candidate,
        candidate_intelligence=candidate_intel
    )

    print("=" * 60)
    print("Matching Engine v2 - 演示")
    print("=" * 60)

    print(f"\n【匹配结果】")
    print(f"  基础匹配分：{result.score.base_score}")
    print(f"  超预期惊喜分：{result.score.surprise_score}")
    print(f"  最终综合分：{result.composite_score}")
    print(f"  招聘者满意分：{result.score.recruiter_satisfaction}")
    print(f"  候选人满意分：{result.score.candidate_satisfaction}")
    print(f"  触发承诺机制：{'是' if result.commitment_triggered else '否'}")
    print(f"  推荐理由：{result.recommendation_reason}")


if __name__ == "__main__":
    demo()