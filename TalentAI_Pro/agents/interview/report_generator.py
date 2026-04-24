"""
Report Generator - 报告生成器

生成结构化面试报告
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from .evaluation_engine import InterviewEvaluation, QuestionEvaluation
from . import EVALUATION_DIMENSIONS


@dataclass
class InterviewReport:
    """
    面试报告

    包含完整面试评估的结构化报告
    """
    report_id: str
    interview_id: str
    candidate_id: str
    candidate_name: str
    job_title: str
    interview_date: str
    interviewer: str = "AI Interview Agent"

    # 评分
    overall_score: float = 0.0
    recommendation: str = ""

    # 维度得分
    dimension_breakdown: Dict[str, Any] = field(default_factory=dict)

    # 各问题评估
    question_evaluations: List[Dict[str, Any]] = field(default_factory=list)

    # 优缺点
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)

    # 详细评语
    summary: str = ""
    detailed_feedback: Dict[str, str] = field(default_factory=dict)

    # 原始数据
    raw_evaluation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "interview_id": self.interview_id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "job_title": self.job_title,
            "interview_date": self.interview_date,
            "interviewer": self.interviewer,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
            "dimension_breakdown": self.dimension_breakdown,
            "question_evaluations": self.question_evaluations,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "summary": self.summary,
            "detailed_feedback": self.detailed_feedback
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        md = f"""# 面试评估报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 报告编号 | {self.report_id} |
| 面试ID | {self.interview_id} |
| 候选人 | {self.candidate_name} |
| 应聘职位 | {self.job_title} |
| 面试日期 | {self.interview_date} |
| 面试官 | {self.interviewer} |

## 综合评估

**总体评分: {self.overall_score}/5.0**

**推荐级别: {self.recommendation}**

### 维度得分

| 维度 | 得分 | 评价 |
|------|------|------|
"""
        for dim_key, dim_info in self.dimension_breakdown.items():
            md += f"| {dim_info['name']} | {dim_info['score']}/5.0 | {dim_info['level_description']} |\n"

        md += f"""
## 优势

"""
        for s in self.strengths:
            md += f"- {s}\n"

        md += f"""
## 待改进

"""
        for c in self.concerns:
            md += f"- {c}\n"

        md += f"""
## 总结

{self.summary}

---

*本报告由 AI Interview Agent 自动生成*
"""
        return md


class ReportGenerator:
    """
    面试报告生成器

    将评估结果转换为结构化报告
    """

    def __init__(self):
        pass

    def generate(
        self,
        evaluation: InterviewEvaluation,
        candidate_name: str,
        job_title: str,
        interview_date: Optional[str] = None
    ) -> InterviewReport:
        """
        生成面试报告

        Args:
            evaluation: 面试评估结果
            candidate_name: 候选人姓名
            job_title: 应聘职位
            interview_date: 面试日期

        Returns:
            InterviewReport: 面试报告
        """
        import uuid

        report_id = str(uuid.uuid4())

        # 维度详情
        dimension_breakdown = {}
        for dim_key, dim_score in evaluation.dimension_scores.items():
            dim_info = EVALUATION_DIMENSIONS.get(dim_key, {})
            dimension_breakdown[dim_key] = {
                "name": dim_score.dimension_name,
                "score": dim_score.score,
                "weight": dim_info.get("weight", 0),
                "level_description": dim_score.level_description,
                "evidence": dim_score.evidence
            }

        # 问题评估详情
        question_evaluations = []
        for qe in evaluation.question_evaluations:
            question_evaluations.append({
                "question_id": qe.question_id,
                "question": qe.question,
                "answer_preview": qe.answer[:200] + "..." if len(qe.answer) > 200 else qe.answer,
                "quality": qe.quality.value,
                "score": qe.overall_score,
                "coverage_score": qe.coverage_score,
                "depth_score": qe.depth_score,
                "feedback": qe.feedback,
                "keywords_found": qe.technical_keywords_found
            })

        # 生成详细反馈
        detailed_feedback = self._generate_detailed_feedback(
            evaluation, question_evaluations
        )

        report = InterviewReport(
            report_id=report_id,
            interview_id=evaluation.interview_id,
            candidate_id=evaluation.candidate_id,
            candidate_name=candidate_name,
            job_title=job_title,
            interview_date=interview_date or datetime.now().strftime("%Y-%m-%d"),
            overall_score=evaluation.overall_score,
            recommendation=evaluation.recommendation,
            dimension_breakdown=dimension_breakdown,
            question_evaluations=question_evaluations,
            strengths=evaluation.strengths,
            concerns=evaluation.concerns,
            summary=evaluation.summary,
            detailed_feedback=detailed_feedback,
            raw_evaluation=evaluation.to_dict()
        )

        return report

    def _generate_detailed_feedback(
        self,
        evaluation: InterviewEvaluation,
        question_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """生成各维度详细反馈"""
        feedback = {}

        # 技术深度反馈
        if "technical_depth" in evaluation.dimension_scores:
            tech_score = evaluation.dimension_scores["technical_depth"].score
            if tech_score >= 4.5:
                feedback["technical_depth"] = "候选人在技术方面表现卓越，对核心概念有深入理解，能够举一反三，具备解决复杂技术问题的能力。"
            elif tech_score >= 3.5:
                feedback["technical_depth"] = "技术基础扎实，对相关技术栈有较好的掌握，能够应对常规开发任务。"
            else:
                feedback["technical_depth"] = "技术理解还需加强，建议系统学习相关技术栈的核心原理。"

        # 问题解决反馈
        if "problem_solving" in evaluation.dimension_scores:
            ps_score = evaluation.dimension_scores["problem_solving"].score
            if ps_score >= 4.5:
                feedback["problem_solving"] = "问题分析能力强，能够快速定位问题根源，提出创新性解决方案。"
            elif ps_score >= 3.5:
                feedback["problem_solving"] = "具备一定的问题解决能力，能够独立处理常见问题。"
            else:
                feedback["problem_solving"] = "问题解决能力有待提高，需要培养更系统的分析方法。"

        # 沟通反馈
        if "communication" in evaluation.dimension_scores:
            comm_score = evaluation.dimension_scores["communication"].score
            if comm_score >= 4.5:
                feedback["communication"] = "表达清晰流畅，逻辑严密，能够有效传达复杂技术概念。"
            elif comm_score >= 3.5:
                feedback["communication"] = "沟通表达能力良好，能够清晰表达想法。"
            else:
                feedback["communication"] = "建议提高沟通表达能力，练习清晰阐述技术方案。"

        return feedback

    def generate_comparison(
        self,
        reports: List[InterviewReport]
    ) -> Dict[str, Any]:
        """
        生成候选人对比报告

        Args:
            reports: 多个候选人的面试报告

        Returns:
            对比分析结果
        """
        if not reports:
            return {}

        # 排序
        sorted_reports = sorted(
            reports,
            key=lambda x: x.overall_score,
            reverse=True
        )

        comparison = {
            "total_candidates": len(reports),
            "average_score": sum(r.overall_score for r in reports) / len(reports),
            "ranking": [
                {
                    "rank": i + 1,
                    "candidate_name": r.candidate_name,
                    "overall_score": r.overall_score,
                    "recommendation": r.recommendation
                }
                for i, r in enumerate(sorted_reports)
            ],
            "dimension_comparison": self._compare_dimensions(reports),
            "recommendation": self._generate_comparison_recommendation(sorted_reports)
        }

        return comparison

    def _compare_dimensions(
        self,
        reports: List[InterviewReport]
    ) -> Dict[str, Any]:
        """对比各维度得分"""
        dimensions = ["technical_depth", "problem_solving", "communication", "culture_fit", "growth_potential"]
        comparison = {}

        for dim in dimensions:
            scores = []
            for r in reports:
                if dim in r.dimension_breakdown:
                    scores.append({
                        "name": r.candidate_name,
                        "score": r.dimension_breakdown[dim]["score"]
                    })

            if scores:
                scores_sorted = sorted(scores, key=lambda x: x["score"], reverse=True)
                comparison[dim] = {
                    "scores": scores_sorted,
                    "best": scores_sorted[0] if scores_sorted else None
                }

        return comparison

    def _generate_comparison_recommendation(
        self,
        sorted_reports: List[InterviewReport]
    ) -> str:
        """生成对比建议"""
        if not sorted_reports:
            return "暂无候选人数据"

        top = sorted_reports[0]

        if top.overall_score >= 4.5:
            return f"强烈推荐 {top.candidate_name}，综合评分 {top.overall_score}，各方面表现优异。"
        elif top.overall_score >= 4.0:
            return f"推荐 {top.candidate_name}，综合评分 {top.overall_score}，适合该职位。"
        else:
            return f"建议进一步面试 {top.candidate_name}，综合评分 {top.overall_score}，可在决定前对比其他机会。"


# 便捷函数
def generate_report(
    evaluation: InterviewEvaluation,
    candidate_name: str,
    job_title: str,
    interview_date: Optional[str] = None
) -> InterviewReport:
    """生成面试报告的便捷函数"""
    generator = ReportGenerator()
    return generator.generate(evaluation, candidate_name, job_title, interview_date)


def generate_markdown_report(report: InterviewReport) -> str:
    """生成Markdown格式报告"""
    return report.to_markdown()