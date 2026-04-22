"""
匹配引擎 v1 - 基础匹配分计算
不含超预期惊喜分，专注核心匹配逻辑

功能：
1. 技能匹配
2. 经验匹配
3. 地点匹配
4. 薪资匹配
5. 综合评分
"""
from typing import Dict, List, Optional, Any, Tuple
import math
import uuid
from datetime import datetime

from ..models.job import Job, JDIntelligence
from ..models.candidate import Candidate, CandidateIntelligence
from ..models.match import MatchResult, MatchScore, MatchConfidence


class MatchingEngineV1:
    """匹配引擎 v1 - 基础版"""

    def __init__(self, threshold: float = 75.0):
        """
        初始化匹配引擎

        Args:
            threshold: 触发阈值，默认75分
        """
        self.threshold = threshold

    def match(self, job: Job, candidate: Candidate) -> MatchResult:
        """
        执行匹配

        Args:
            job: 职位对象
            candidate: 候选人对象

        Returns:
            MatchResult: 匹配结果
        """
        # 1. 计算各维度匹配分
        skill_match = self._calculate_skill_match(job, candidate)
        experience_match = self._calculate_experience_match(job, candidate)
        location_match = self._calculate_location_match(job, candidate)
        salary_match = self._calculate_salary_match(job, candidate)

        # 2. 计算基础匹配分（加权平均）
        base_score = (
            skill_match * 0.4 +
            experience_match * 0.3 +
            location_match * 0.15 +
            salary_match * 0.15
        )

        # 3. 双向满意分计算
        recruiter_satisfaction = self._calculate_recruiter_satisfaction(
            job, candidate, skill_match, experience_match
        )
        candidate_satisfaction = self._calculate_candidate_satisfaction(
            job, candidate, location_match, salary_match
        )

        # 4. 计算综合撮合分
        # 公式：招聘者满意分 × √(候选人满意分)
        composite_score = recruiter_satisfaction * math.sqrt(candidate_satisfaction / 100)

        # 5. 构建评分对象
        score = MatchScore(
            base_score=round(base_score, 2),
            surprise_score=0,  # v1不含超预期分
            final_score=round(base_score, 2),
            recruiter_satisfaction=round(recruiter_satisfaction, 2),
            candidate_satisfaction=round(candidate_satisfaction, 2),
            skill_match_details={"skill_match": round(skill_match, 2)},
            experience_match=round(experience_match, 2),
            location_match=round(location_match, 2),
            salary_match=round(salary_match, 2),
            confidence=self._get_confidence(skill_match, experience_match)
        )

        # 6. 判断触发条件
        commitment_triggered = composite_score >= self.threshold

        # 7. 构建匹配结果
        result = MatchResult(
            id=f"MATCH-{uuid.uuid4().hex[:8].upper()}",
            job_id=job.id,
            candidate_id=candidate.id,
            score=score,
            commitment_triggered=commitment_triggered,
            recruiter_threshold_met=recruiter_satisfaction >= self.threshold,
            candidate_threshold_met=candidate_satisfaction >= self.threshold,
            composite_score=round(composite_score, 2),
            recommendation_reason=self._generate_recommendation(
                job, candidate, base_score, composite_score
            )
        )

        return result

    def batch_match(
        self, job: Job, candidates: List[Candidate]
    ) -> List[MatchResult]:
        """
        批量匹配

        Args:
            job: 职位对象
            candidates: 候选人列表

        Returns:
            List[MatchResult]: 匹配结果列表，按综合撮合分降序排列
        """
        results = [self.match(job, candidate) for candidate in candidates]
        # 按综合撮合分降序排列
        results.sort(key=lambda x: x.composite_score, reverse=True)
        return results

    def _calculate_skill_match(self, job: Job, candidate: Candidate) -> float:
        """计算技能匹配分"""
        if not job.required_skills:
            return 80.0  # 无要求，默认80

        candidate_skills = self._extract_candidate_skills(candidate)
        if not candidate_skills:
            return 30.0  # 无法判断，低分

        # 精确匹配
        matched = sum(1 for skill in job.required_skills
                       if any(skill.lower() in cs.lower() or cs.lower() in skill.lower()
                              for cs in candidate_skills))

        # 部分匹配（优先技能）
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

        # 从当前职位提取
        if candidate.current_title:
            skills.append(candidate.current_title)

        # 从GitHub数据提取
        if candidate.github_data and "skills" in candidate.github_data:
            skills.extend(candidate.github_data["skills"])

        # 从LinkedIn数据提取
        if candidate.linkedin_data and "skills" in candidate.linkedin_data:
            skills.extend(candidate.linkedin_data["skills"])

        return list(set(skills))

    def _calculate_experience_match(
        self, job: Job, candidate: Candidate
    ) -> float:
        """计算经验匹配分"""
        if not job.min_experience_years:
            return 80.0  # 无要求，默认80

        candidate_years = getattr(candidate, "years_of_experience", 0)

        if candidate_years >= job.min_experience_years:
            # 超过要求越多，适当扣分（over-qualified）
            excess = candidate_years - job.min_experience_years
            if excess <= 2:
                return 90.0
            elif excess <= 5:
                return 80.0
            else:
                return 70.0
        else:
            # 经验不足
            deficit = job.min_experience_years - candidate_years
            return max(0, 80 - deficit * 10)

    def _calculate_location_match(self, job: Job, candidate: Candidate) -> float:
        """计算地点匹配分"""
        if not job.location:
            return 80.0

        candidate_locations = candidate.preferred_locations or []
        if not candidate_locations:
            # 如果候选人没有偏好地点，检查当前地点
            if candidate.location:
                candidate_locations = [candidate.location]
            else:
                return 70.0  # 无法判断

        # 完全匹配
        for loc in candidate_locations:
            if job.location in loc or loc in job.location:
                return 100.0

        # 同城匹配（北京 vs 北京）
        if self._same_city(job.location, candidate_locations):
            return 80.0

        return 40.0  # 不匹配

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
            return 70.0  # 无薪资信息，默认70

        candidate_expected_min = candidate.expected_salary_min or 0
        candidate_expected_max = candidate.expected_salary_max or 999999

        # 检查是否有交集
        if candidate_expected_max < job.salary_min:
            return 30.0  # 候选人期望低于职位下限
        elif candidate_expected_min > job.salary_max:
            return 50.0  # 候选人期望高于职位上限（可能有股权等补偿）
        else:
            # 有交集，高分
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

    def _get_confidence(self, skill_match: float, experience_match: float) -> MatchConfidence:
        """获取匹配置信度"""
        avg = (skill_match + experience_match) / 2
        if avg >= 80:
            return MatchConfidence.HIGH
        elif avg >= 60:
            return MatchConfidence.MEDIUM
        else:
            return MatchConfidence.LOW

    def _generate_recommendation(
        self, job: Job, candidate: Candidate, base_score: float, composite_score: float
    ) -> str:
        """生成推荐理由"""
        if composite_score >= 75:
            return f"强力推荐：候选人与职位高度匹配，综合撮合分{composite_score:.1f}，超过触发阈值75"
        elif composite_score >= 60:
            return f"建议尝试：候选人与职位有一定匹配度，综合撮合分{composite_score:.1f}"
        else:
            return f"暂不推荐：匹配度较低，综合撮合分{composite_score:.1f}，建议寻找更合适的候选人"
