"""
LLM Semantic Matching - 语义匹配模块
=====================================

基于LLM的语义匹配能力，增强传统关键词匹配

Usage:
    from TalentAI_Pro.llm.semantic_matching import LLMSemanticMatching

    matcher = LLMSemanticMatching(gateway)
    result = await matcher.match JD(job_description, candidate_resume)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

from .gateway import LLMGateway, Message


@dataclass
class SemanticMatchResult:
    """语义匹配结果"""
    overall_score: float              # 0-100
    skill_match_score: float          # 技能匹配度
    experience_match_score: float      # 经验匹配度
    hidden_strengths: List[str]        # 隐藏优势
    gaps: List[str]                   # 差距/不足
    reasoning: str                    # 匹配理由
    recommendation: str               # 推荐建议

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "skill_match_score": self.skill_match_score,
            "experience_match_score": self.experience_match_score,
            "hidden_strengths": self.hidden_strengths,
            "gaps": self.gaps,
            "reasoning": self.reasoning,
            "recommendation": self.recommendation,
        }


class LLMSemanticMatching:
    """
    基于LLM的语义匹配

    替代传统关键词匹配，实现：
    1. 深层语义理解技能相关性
    2. 发现简历中的隐藏优势
    3. 识别真实经验差距
    4. 生成个性化匹配理由
    """

    SKILL_MATCH_PROMPT = """你是一个专业的HR技术面试官，负责评估候选人与职位的技能匹配度。

请分析以下职位要求和候选人技能，判断深层匹配关系。

职位要求技能: {required_skills}
候选人技能: {candidate_skills}

请以JSON格式返回分析结果：
{{
    "skill_match_score": 0-100的匹配分数,
    "deep_matches": ["深层匹配的技能对及原因"],
    "partial_matches": ["部分匹配的技能"],
    "missing_critical": ["缺失的关键技能"],
    "transferable_skills": ["可迁移技能"],
    "analysis": "详细分析说明"
}}

注意：
- 不仅看技能名称匹配，要分析深层相关性
- 考虑候选人的学习能力和技术迁移能力
- 识别看似不相关但实际有价值的技能"""

    EXPERIENCE_MATCH_PROMPT = """你是一个资深HR，负责评估候选人经验与职位的匹配度。

职位信息:
- 职位名称: {job_title}
- 职级要求: {level}
- 核心职责: {responsibilities}
- 所需经验: {required_years}年

候选人背景:
- 当前职位: {current_title}
- 工作年限: {years}年
- 主要成就: {achievements}

请以JSON格式返回：
{{
    "experience_match_score": 0-100,
    "alignment_level": "完全匹配/高度匹配/基本匹配/差距较大",
    "relevant_experience": ["相关经验"],
    "overkill_concerns": ["过度资深可能带来的问题"],
    "growth_potential": "候选人成长空间评估",
    "reasoning": "评估理由"
}}"""

    OVERALL_MATCH_PROMPT = """你是一个招聘专家，负责判断候选人与职位的整体匹配度。

候选人: {candidate_name}
当前职位: {current_title}
工作年限: {years}年
技能: {skills}

职位: {job_title}
公司: {company_name}
要求: {requirements}

候选人自述优势:
{strengths}

请以JSON格式返回最终匹配评估：
{{
    "overall_score": 0-100,
    "mutual_fit": {{
        "recruiter_fit": 0-100,
        "candidate_fit": 0-100
    }},
    "hidden_strengths": ["候选人让你惊喜的隐藏优势"],
    "gaps": ["需要关注的不匹配点"],
    "reasoning": "综合匹配理由",
    "recommendation": "强烈推荐/推荐/可考虑/不建议",
    "interview_focus": ["面试重点考察方向"]
}}"""

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def match_skills(
        self,
        required_skills: List[str],
        candidate_skills: List[str],
    ) -> Dict[str, Any]:
        """
        技能语义匹配

        Args:
            required_skills: 职位要求的技能列表
            candidate_skills: 候选人具备的技能列表

        Returns:
            dict: 技能匹配分析结果
        """
        prompt = self.SKILL_MATCH_PROMPT.format(
            required_skills=", ".join(required_skills),
            candidate_skills=", ".join(candidate_skills),
        )

        try:
            response = await self.gateway.chat(
                prompt=prompt,
                system="你是一个专业的技术招聘专家",
                model="qwen3-omni",
                temperature=0.3,
            )

            return self._parse_json_response(response.content)

        except Exception as e:
            return {
                "skill_match_score": 50,
                "analysis": f"技能匹配分析失败: {str(e)}",
                "error": True,
            }

    async def match_experience(
        self,
        job_info: Dict[str, Any],
        candidate_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        经验匹配分析

        Args:
            job_info: 职位信息
            candidate_info: 候选人信息

        Returns:
            dict: 经验匹配结果
        """
        prompt = self.EXPERIENCE_MATCH_PROMPT.format(
            job_title=job_info.get("title", ""),
            level=job_info.get("level", ""),
            responsibilities=job_info.get("responsibilities", ""),
            required_years=job_info.get("min_experience_years", 0),
            current_title=candidate_info.get("current_title", ""),
            years=candidate_info.get("years_of_experience", 0),
            achievements=candidate_info.get("achievements", ""),
        )

        try:
            response = await self.gateway.chat(
                prompt=prompt,
                system="你是一个资深HR招聘专家",
                model="qwen3-omni",
                temperature=0.3,
            )

            return self._parse_json_response(response.content)

        except Exception as e:
            return {
                "experience_match_score": 50,
                "reasoning": f"经验匹配分析失败: {str(e)}",
                "error": True,
            }

    async def overall_match(
        self,
        job_info: Dict[str, Any],
        candidate_info: Dict[str, Any],
    ) -> SemanticMatchResult:
        """
        整体匹配评估

        Args:
            job_info: 职位信息
            candidate_info: 候选人信息

        Returns:
            SemanticMatchResult: 完整匹配结果
        """
        # 并行执行技能和经验匹配
        skill_task = self.match_skills(
            required_skills=job_info.get("required_skills", []),
            candidate_skills=candidate_info.get("skills", []),
        )

        exp_task = self.match_experience(
            job_info=job_info,
            candidate_info=candidate_info,
        )

        skill_result, exp_result = await self._run_parallel(skill_task, exp_task)

        # 构建综合评估prompt
        prompt = self.OVERALL_MATCH_PROMPT.format(
            candidate_name=candidate_info.get("name", ""),
            current_title=candidate_info.get("current_title", ""),
            years=candidate_info.get("years_of_experience", 0),
            skills=", ".join(candidate_info.get("skills", [])),
            job_title=job_info.get("title", ""),
            company_name=job_info.get("company_name", ""),
            requirements=f"技能: {', '.join(job_info.get('required_skills', []))}, "
                       f"经验: {job_info.get('min_experience_years', 0)}年",
            strengths=candidate_info.get("strengths", "未提供"),
        )

        try:
            response = await self.gateway.chat(
                prompt=prompt,
                system="你是一个专业的招聘评估专家",
                model="qwen3-omni",
                temperature=0.3,
            )

            overall_result = self._parse_json_response(response.content)

            return SemanticMatchResult(
                overall_score=overall_result.get("overall_score", 50),
                skill_match_score=skill_result.get("skill_match_score", 50),
                experience_match_score=exp_result.get("experience_match_score", 50),
                hidden_strengths=overall_result.get("hidden_strengths", []),
                gaps=overall_result.get("gaps", []),
                reasoning=overall_result.get("reasoning", ""),
                recommendation=overall_result.get("recommendation", "可考虑"),
            )

        except Exception as e:
            return SemanticMatchResult(
                overall_score=50,
                skill_match_score=skill_result.get("skill_match_score", 50),
                experience_match_score=exp_result.get("experience_match_score", 50),
                hidden_strengths=[],
                gaps=["LLM匹配分析失败"],
                reasoning=str(e),
                recommendation="无法评估",
            )

    async def batch_match(
        self,
        job_info: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> List[SemanticMatchResult]:
        """
        批量匹配

        Args:
            job_info: 职位信息
            candidates: 候选人列表

        Returns:
            List[SemanticMatchResult]: 按匹配度排序的结果
        """
        results = []
        for candidate in candidates:
            result = await self.overall_match(job_info, candidate)
            results.append(result)

        # 按总分排序
        results.sort(key=lambda x: x.overall_score, reverse=True)
        return results

    async def suggest_interview_focus(
        self,
        job_info: Dict[str, Any],
        candidate_info: Dict[str, Any],
    ) -> List[str]:
        """
        基于匹配分析，生成面试重点考察方向

        Args:
            job_info: 职位信息
            candidate_info: 候选人信息

        Returns:
            List[str]: 面试问题/考察方向列表
        """
        prompt = f"""基于以下候选人与职位的匹配分析，生成面试重点考察方向：

职位: {job_info.get('title', '')}
要求技能: {', '.join(job_info.get('required_skills', []))}

候选人: {candidate_info.get('name', '')}
背景: {candidate_info.get('current_title', '')}
技能: {', '.join(candidate_info.get('skills', []))}
潜在差距: {', '.join(candidate_info.get('gaps', []))}

请生成5个具体的面试考察点，每个考察点要：
1. 针对候选人的薄弱环节
2. 设计追问深入了解
3. 验证候选人真实能力

以JSON格式返回：
{{
    "focus_areas": [
        {{
            "topic": "考察主题",
            "question": "具体问题",
            "follow_up": "追问方向",
            "目的": "考察目的"
        }}
    ]
}}"""

        try:
            response = await self.gateway.chat(
                prompt=prompt,
                system="你是一个专业的面试官",
                model="qwen3-omni",
                temperature=0.5,
            )

            result = self._parse_json_response(response.content)
            return result.get("focus_areas", [])

        except Exception as e:
            return [{
                "topic": "技能验证",
                "question": "请详细描述你在这项技能上的项目经验",
                "follow_up": "遇到过最大的挑战是什么？",
                "目的": "验证简历真实性",
            }]

    async def _run_parallel(self, *tasks):
        """运行多个异步任务"""
        import asyncio
        return await asyncio.gather(*tasks)

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            # 提取JSON块
            json_str = self._extract_json(content)
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": True, "raw_content": content[:500]}

    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON"""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            return text[start:end]

        return text.strip()
