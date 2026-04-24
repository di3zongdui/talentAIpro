"""
Evaluation Engine - 评估引擎

对候选人的回答进行实时评估
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from . import EVALUATION_DIMENSIONS, RECOMMENDATION_LEVELS


class AnswerQuality(Enum):
    """回答质量等级"""
    EXCELLENT = "excellent"      # 优秀 - 完美回答
    GOOD = "good"                # 良好 - 完整回答
    AVERAGE = "average"           # 一般 - 基本回答
    POOR = "poor"                # 较差 - 部分回答
    FAIL = "fail"                # 不及格 - 未能回答


@dataclass
class DimensionScore:
    """维度评分"""
    dimension: str
    dimension_name: str
    score: float                 # 1-5分
    level_description: str
    evidence: str                # 评分依据
    keywords_matched: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "dimension_name": self.dimension_name,
            "score": self.score,
            "level_description": self.level_description,
            "evidence": self.evidence,
            "keywords_matched": self.keywords_matched,
            "improvement_suggestions": self.improvement_suggestions
        }


@dataclass
class QuestionEvaluation:
    """单个问题的评估结果"""
    question_id: str
    question: str
    answer: str
    quality: AnswerQuality
    technical_keywords_found: List[str] = field(default_factory=list)
    technical_keywords_expected: List[str] = field(default_factory=list)
    coverage_score: float = 0.0   # 0-1，覆盖度
    depth_score: float = 0.0     # 0-1，深度
    overall_score: float = 0.0   # 1-5，综合评分
    feedback: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question,
            "answer": self.answer,
            "quality": self.quality.value,
            "technical_keywords_found": self.technical_keywords_found,
            "technical_keywords_expected": self.technical_keywords_expected,
            "coverage_score": self.coverage_score,
            "depth_score": self.depth_score,
            "overall_score": self.overall_score,
            "feedback": self.feedback
        }


@dataclass
class InterviewEvaluation:
    """完整面试评估"""
    interview_id: str
    candidate_id: str
    overall_score: float          # 1-5分
    recommendation: str          # 推荐级别
    dimension_scores: Dict[str, DimensionScore]
    question_evaluations: List[QuestionEvaluation]
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "candidate_id": self.candidate_id,
            "overall_score": round(self.overall_score, 2),
            "recommendation": self.recommendation,
            "dimension_scores": {
                k: v.to_dict() for k, v in self.dimension_scores.items()
            },
            "question_evaluations": [q.to_dict() for q in self.question_evaluations],
            "strengths": self.strengths,
            "concerns": self.concerns,
            "summary": self.summary
        }


class EvaluationEngine:
    """
    面试评估引擎

    对候选人的回答进行多维度评估
    """

    def __init__(self):
        self.dimensions = EVALUATION_DIMENSIONS
        self.recommendation_levels = RECOMMENDATION_LEVELS

    def evaluate_answer(
        self,
        question: Dict[str, Any],
        answer: str,
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> QuestionEvaluation:
        """
        评估单个问题的回答

        Args:
            question: 问题对象
            answer: 候选人回答
            candidate_profile: 候选人背景（用于校准期望）

        Returns:
            QuestionEvaluation: 问题评估结果
        """
        category = question.get("category", "technical")

        if category == "behavioral":
            return self._evaluate_behavioral(question, answer)
        else:
            return self._evaluate_technical(question, answer)

    def _evaluate_technical(
        self,
        question: Dict[str, Any],
        answer: str
    ) -> QuestionEvaluation:
        """评估技术问题回答"""
        expected_keywords = question.get("expected_keywords", [])
        difficulty = question.get("difficulty", 3)

        # 关键词匹配
        keywords_found = []
        answer_lower = answer.lower()
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                keywords_found.append(keyword)

        # 计算覆盖度
        coverage = len(keywords_found) / max(len(expected_keywords), 1)

        # 计算深度（简单版：基于回答长度和关键词密度）
        answer_length = len(answer)
        keyword_density = len(keywords_found) / max(answer_length / 100, 1)
        depth = min(coverage * 0.6 + keyword_density * 0.4, 1.0)

        # 综合评分
        base_score = (coverage * 0.5 + depth * 0.5) * 5
        # 根据难度调整
        if difficulty >= 4:
            # 高难度问题，期望更高
            base_score = base_score * 0.9

        overall_score = round(min(max(base_score, 1.0), 5.0), 1)

        # 质量等级
        if overall_score >= 4.5:
            quality = AnswerQuality.EXCELLENT
        elif overall_score >= 3.5:
            quality = AnswerQuality.GOOD
        elif overall_score >= 2.5:
            quality = AnswerQuality.AVERAGE
        elif overall_score >= 1.5:
            quality = AnswerQuality.POOR
        else:
            quality = AnswerQuality.FAIL

        # 生成反馈
        feedback = self._generate_technical_feedback(
            keywords_found, expected_keywords, quality
        )

        return QuestionEvaluation(
            question_id=question.get("id", ""),
            question=question.get("question", ""),
            answer=answer,
            quality=quality,
            technical_keywords_found=keywords_found,
            technical_keywords_expected=expected_keywords,
            coverage_score=round(coverage, 2),
            depth_score=round(depth, 2),
            overall_score=overall_score,
            feedback=feedback
        )

    def _evaluate_behavioral(
        self,
        question: Dict[str, Any],
        answer: str
    ) -> QuestionEvaluation:
        """评估行为面试问题回答"""
        # STAR框架完整性评估
        star_elements = {
            "situation": False,  # 情境
            "task": False,        # 任务
            "action": False,      # 行动
            "result": False       # 结果
        }

        answer_lower = answer.lower()

        # 检测STAR元素（简化版）
        star_keywords = {
            "situation": ["当时", "情况", "背景", "项目", "公司", "团队"],
            "task": ["需要", "目标", "我的职责", "负责", "面临"],
            "action": ["我", "做了", "采取", "实施", "推动", "带领"],
            "result": ["结果", "成果", "实现了", "达成了", "提升了", "最终"]
        }

        for element, keywords in star_keywords.items():
            for keyword in keywords:
                if keyword in answer_lower:
                    star_elements[element] = True
                    break

        # 计算STAR完整度
        star_coverage = sum(star_elements.values()) / 4

        # 回答长度评估
        answer_length = len(answer)
        length_score = min(answer_length / 500, 1.0)  # 500字为满分

        # 综合评分
        overall_score = round(star_coverage * 0.6 + length_score * 0.4 * 5, 1)

        # 质量等级
        if overall_score >= 4.5:
            quality = AnswerQuality.EXCELLENT
        elif overall_score >= 3.5:
            quality = AnswerQuality.GOOD
        elif overall_score >= 2.5:
            quality = AnswerQuality.AVERAGE
        elif overall_score >= 1.5:
            quality = AnswerQuality.POOR
        else:
            quality = AnswerQuality.FAIL

        # 生成反馈
        missing_elements = [k for k, v in star_elements.items() if not v]
        if missing_elements:
            feedback = f"STAR框架完整度 {int(star_coverage*100)}%。建议补充: {', '.join(missing_elements)}"
        else:
            feedback = "STAR框架完整，描述清晰具体。"

        return QuestionEvaluation(
            question_id=question.get("id", ""),
            question=question.get("question", ""),
            answer=answer,
            quality=quality,
            technical_keywords_found=[],
            technical_keywords_expected=[],
            coverage_score=round(star_coverage, 2),
            depth_score=round(length_score, 2),
            overall_score=overall_score,
            feedback=feedback
        )

    def _generate_technical_feedback(
        self,
        keywords_found: List[str],
        expected_keywords: List[str],
        quality: AnswerQuality
    ) -> str:
        """生成技术问题反馈"""
        coverage = len(keywords_found) / max(len(expected_keywords), 1)

        if quality == AnswerQuality.EXCELLENT:
            return f"完美回答。覆盖了所有关键概念: {', '.join(keywords_found)}"
        elif quality == AnswerQuality.GOOD:
            if coverage >= 0.7:
                return f"回答良好。已覆盖核心概念: {', '.join(keywords_found)}"
            else:
                return f"基本正确。建议补充: {', '.join(set(expected_keywords) - set(keywords_found))}"
        elif quality == AnswerQuality.AVERAGE:
            missing = set(expected_keywords) - set(keywords_found)
            if missing:
                return f"理解基本概念，但有遗漏。建议深入了解: {', '.join(missing)}"
            return "理解基本概念，可以进一步深入。"
        else:
            return "建议加强对核心概念的理解。"

    def evaluate_interview(
        self,
        interview_id: str,
        candidate_id: str,
        question_evaluations: List[QuestionEvaluation],
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> InterviewEvaluation:
        """
        评估完整面试

        Args:
            interview_id: 面试ID
            candidate_id: 候选人ID
            question_evaluations: 所有问题的评估结果
            candidate_profile: 候选人背景

        Returns:
            InterviewEvaluation: 完整面试评估
        """
        # 1. 计算各维度加权得分
        dimension_scores = self._calculate_dimension_scores(question_evaluations)

        # 2. 计算总体得分
        overall_score = self._calculate_overall_score(dimension_scores)

        # 3. 确定推荐级别
        recommendation = self._get_recommendation(overall_score)

        # 4. 提取优缺点
        strengths, concerns = self._extract_strengths_concerns(question_evaluations)

        # 5. 生成总结
        summary = self._generate_summary(
            overall_score, recommendation, strengths, concerns
        )

        return InterviewEvaluation(
            interview_id=interview_id,
            candidate_id=candidate_id,
            overall_score=overall_score,
            recommendation=recommendation,
            dimension_scores=dimension_scores,
            question_evaluations=question_evaluations,
            strengths=strengths,
            concerns=concerns,
            summary=summary
        )

    def _calculate_dimension_scores(
        self,
        question_evaluations: List[QuestionEvaluation]
    ) -> Dict[str, DimensionScore]:
        """计算各维度得分"""
        # 简单映射：技术问题评估 technical_depth 和 problem_solving
        # 行为问题评估 communication 和 culture_fit

        technical_scores = []
        behavioral_scores = []

        for q_eval in question_evaluations:
            if "b-" in q_eval.question_id:  # behavioral
                behavioral_scores.append(q_eval.overall_score)
            else:
                technical_scores.append(q_eval.overall_score)

        avg_technical = sum(technical_scores) / max(len(technical_scores), 1)
        avg_behavioral = sum(behavioral_scores) / max(len(behavioral_scores), 1)

        # 按权重分配
        dimension_scores = {}

        for dim_key, dim_info in self.dimensions.items():
            if dim_key == "technical_depth":
                score = avg_technical
            elif dim_key == "problem_solving":
                score = avg_technical * 0.9  # 略低
            elif dim_key == "communication":
                score = avg_behavioral
            elif dim_key == "culture_fit":
                score = avg_behavioral * 0.95
            else:  # growth_potential
                score = (avg_technical + avg_behavioral) / 2

            level_desc = dim_info["levels"].get(int(round(score)), "")

            dimension_scores[dim_key] = DimensionScore(
                dimension=dim_key,
                dimension_name=dim_info["name"],
                score=round(score, 1),
                level_description=level_desc,
                evidence=f"基于{len(question_evaluations)}道问题的平均表现"
            )

        return dimension_scores

    def _calculate_overall_score(
        self,
        dimension_scores: Dict[str, DimensionScore]
    ) -> float:
        """计算加权总分"""
        total = 0.0
        for dim_key, dim_info in self.dimensions.items():
            weight = dim_info["weight"]
            score = dimension_scores[dim_key].score
            total += score * weight

        return round(total, 2)

    def _get_recommendation(self, overall_score: float) -> str:
        """获取推荐级别"""
        for (low, high), label in self.recommendation_levels.items():
            if low <= overall_score < high:
                return label
        return "不推荐"

    def _extract_strengths_concerns(
        self,
        question_evaluations: List[QuestionEvaluation]
    ) -> tuple:
        """提取优缺点"""
        strengths = []
        concerns = []

        # 按质量分组
        excellent = [q for q in question_evaluations if q.quality == AnswerQuality.EXCELLENT]
        good = [q for q in question_evaluations if q.quality == AnswerQuality.GOOD]
        poor = [q for q in question_evaluations if q.quality in [AnswerQuality.POOR, AnswerQuality.FAIL]]

        if excellent:
            skills_excellent = set([q.question.get("skill", "该领域") for q in excellent])
            strengths.append(f"在{', '.join(skills_excellent)}表现出色")

        if good:
            skills_good = set([q.question.get("skill", "该领域") for q in good])
            strengths.append(f"{', '.join(skills_good)}理解正确")

        if poor:
            skills_poor = set([q.question.get("skill", "该领域") for q in poor])
            concerns.append(f"{', '.join(skills_poor)}需要加强")

        return strengths, concerns

    def _generate_summary(
        self,
        overall_score: float,
        recommendation: str,
        strengths: List[str],
        concerns: List[str]
    ) -> str:
        """生成评估总结"""
        parts = []

        parts.append(f"综合评分: {overall_score}/5.0 ({recommendation})")

        if strengths:
            parts.append(f"优势: {'; '.join(strengths)}")

        if concerns:
            parts.append(f"待改进: {'; '.join(concerns)}")

        return "。".join(parts)


# 便捷函数
def evaluate_answer(
    question: Dict[str, Any],
    answer: str,
    candidate_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """评估单个回答的便捷函数"""
    engine = EvaluationEngine()
    result = engine.evaluate_answer(question, answer, candidate_profile)
    return result.to_dict()


def evaluate_interview(
    interview_id: str,
    candidate_id: str,
    question_evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """评估完整面试的便捷函数"""
    engine = EvaluationEngine()

    # 转换问题评估
    q_evals = []
    for qe in question_evaluations:
        q_evals.append(QuestionEvaluation(
            question_id=qe.get("question_id", ""),
            question=qe.get("question", ""),
            answer=qe.get("answer", ""),
            quality=AnswerQuality(qe.get("quality", "average")),
            technical_keywords_found=qe.get("technical_keywords_found", []),
            technical_keywords_expected=qe.get("technical_keywords_expected", []),
            coverage_score=qe.get("coverage_score", 0.0),
            depth_score=qe.get("depth_score", 0.0),
            overall_score=qe.get("overall_score", 3.0),
            feedback=qe.get("feedback", "")
        ))

    result = engine.evaluate_interview(
        interview_id, candidate_id, q_evals
    )
    return result.to_dict()