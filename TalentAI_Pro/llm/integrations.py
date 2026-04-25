"""
LLM能力融合模块 - Interview & Negotiation
==========================================

将LLM能力无缝接入现有Agent系统

Usage:
    from TalentAI_Pro.llm.integrations import LLMInterviewIntegration, LLMNegotiationIntegration

    # Interview Agent接入LLM
    interview_llm = LLMInterviewIntegration(gateway)
    evaluation = await interview_llm.evaluate_answer(question, answer, context)

    # Negotiation Engine接入LLM
    negotiation_llm = LLMNegotiationIntegration(gateway)
    message = await negotiation_llm.generate_message(situation, tone)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

from .gateway import LLMGateway, Message


@dataclass
class InterviewEvaluation:
    """面试评估结果"""
    score: float                    # 1-5分
    quality: str                    # excellent/good/average/poor/fail
    keywords_found: List[str]
    keywords_missing: List[str]
    feedback: str
    suggestions: List[str]
    streaming_chunks: List[str] = None  # 流式评估中间结果

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "quality": self.quality,
            "keywords_found": self.keywords_found,
            "keywords_missing": self.keywords_missing,
            "feedback": self.feedback,
            "suggestions": self.suggestions,
        }


class LLMInterviewIntegration:
    """
    Interview Agent的LLM集成

    替代原有的关键词匹配评估，改用LLM进行语义理解
    """

    SYSTEM_PROMPT = """你是一个专业的技术面试官，负责评估候选人的回答质量。

评估维度：
1. 技术深度 - 是否真正理解原理
2. 回答完整性 - 是否覆盖关键点
3. 表达清晰度 - 逻辑是否清晰
4. 实际经验 - 是否有实战佐证

请以JSON格式返回评估结果：
{
    "score": 1-5的评分,
    "quality": "excellent/good/average/poor/fail",
    "keywords_found": ["发现的关键词列表"],
    "keywords_missing": ["缺失的关键概念"],
    "feedback": "详细的书面反馈",
    "suggestions": ["改进建议列表"]
}

注意：
- 只评估技术内容，不评价个人
- 反馈要具体、有建设性
- 评分要客观公正"""

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        context: Dict[str, Any],
        stream_callback=None
    ) -> InterviewEvaluation:
        """
        评估候选人回答

        Args:
            question: 面试问题
            answer: 候选人回答
            context: 上下文（职位要求、难度级别等）
            stream_callback: 流式回调（可选）

        Returns:
            InterviewEvaluation: 评估结果
        """
        # 构建提示
        job_level = context.get("level", "mid")
        required_skills = context.get("required_skills", [])

        user_prompt = f"""职位级别: {job_level}
要求技能: {', '.join(required_skills)}

面试问题: {question}

候选人回答: {answer}

请评估这个回答："""

        try:
            if stream_callback:
                # 流式评估
                chunks = []
                async def wrapper(chunk):
                    chunks.append(chunk)
                    await stream_callback(chunk)

                await self.gateway.stream(
                    prompt=user_prompt,
                    system=self.SYSTEM_PROMPT,
                    callback=wrapper,
                    model="qwen3-omni",
                )

                content = "".join(chunks)
            else:
                # 非流式评估
                response = await self.gateway.chat(
                    prompt=user_prompt,
                    system=self.SYSTEM_PROMPT,
                    model="qwen3-omni",
                )
                content = response.content

            # 解析JSON结果
            return self._parse_evaluation(content, stream_callback is not None)

        except Exception as e:
            # LLM调用失败，返回默认评估
            return InterviewEvaluation(
                score=3.0,
                quality="average",
                keywords_found=[],
                keywords_missing=[],
                feedback=f"评估服务暂时不可用: {str(e)}",
                suggestions=["请稍后重试"],
            )

    def _parse_evaluation(self, content: str, is_streaming: bool = False) -> InterviewEvaluation:
        """解析LLM返回的JSON评估结果"""
        try:
            # 尝试提取JSON
            json_str = self._extract_json(content)
            data = json.loads(json_str)

            return InterviewEvaluation(
                score=float(data.get("score", 3.0)),
                quality=data.get("quality", "average"),
                keywords_found=data.get("keywords_found", []),
                keywords_missing=data.get("keywords_missing", []),
                feedback=data.get("feedback", ""),
                suggestions=data.get("suggestions", []),
                streaming_chunks=[content] if is_streaming else None,
            )
        except json.JSONDecodeError:
            # JSON解析失败，返回文本反馈
            return InterviewEvaluation(
                score=3.0,
                quality="average",
                keywords_found=[],
                keywords_missing=[],
                feedback=content[:500],  # 截取前500字符
                suggestions=[],
            )

    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON"""
        # 尝试找到 ```json ... ``` 块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # 尝试找到 ``` ... ``` 块
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # 尝试找到 { ... } 块
        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            return text[start:end]

        return text.strip()

    async def generate_followup_question(
        self,
        question: str,
        answer: str,
        context: Dict[str, Any]
    ) -> str:
        """基于回答生成追问"""
        user_prompt = f"""面试官问: {question}

候选人回答: {answer}

请生成一个追问问题，深入考察候选人的理解深度。
要求：
- 追问要有深度，不能是表面问题
- 要针对候选人回答中的薄弱点
- 保持专业的面试官语气

直接返回追问问题，不需要其他内容。"""

        response = await self.gateway.chat(
            prompt=user_prompt,
            system="你是一个专业的技术面试官",
            model="qwen3-omni",
        )

        return response.content.strip()


class LLMNegotiationIntegration:
    """
    Negotiation Engine的LLM集成

    替代模板话术，改用LLM生成个性化谈判消息
    """

    TONE_INSTRUCTIONS = {
        "aggressive": "坚定维护公司利益，直接表达底线，但保持专业礼貌。",
        "moderate": "平衡双方利益，寻找共赢方案，展现灵活性。",
        "conciliatory": "积极倾听候选人诉求，展现公司诚意，愿意做出合理让步。",
    }

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def generate_message(
        self,
        situation: str,
        tone: str,
        candidate_info: str,
        company_offer: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        生成谈判消息

        Args:
            situation: 当前谈判情况描述
            tone: 语气风格 (aggressive/moderate/conciliatory)
            candidate_info: 候选人背景信息
            company_offer: 公司Offer详情
            conversation_history: 对话历史（可选）

        Returns:
            str: 生成的谈判消息
        """
        tone_instruction = self.TONE_INSTRUCTIONS.get(tone, self.TONE_INSTRUCTIONS["moderate"])

        # 构建Offer摘要
        offer_summary = self._format_offer(company_offer)

        # 构建对话历史
        history_text = ""
        if conversation_history:
            history_text = "\n对话历史：\n" + "\n".join([
                f"- {h.get('speaker', '未知')}: {h.get('message', '')}"
                for h in conversation_history[-3:]  # 最近3轮
            ])

        user_prompt = f"""当前谈判情况: {situation}
{history_text}

候选人背景: {candidate_info}

公司Offer:
{offer_summary}

语气要求: {tone_instruction}

请生成一条发送给候选人的消息，要求：
1. 100字以内
2. 微信风格，自然友好
3. 不暴露AI身份，用"我"代表公司
4. 要有针对性，不能是通用模板

直接返回消息内容，不要加引号或格式。"""

        response = await self.gateway.chat(
            prompt=user_prompt,
            system="你是一个有10年经验的HR谈判专家，帮助公司在薪资谈判中达成双赢。",
            model="qwen3-omni",
            temperature=0.8,
        )

        return response.content.strip()

    async def analyze_candidate_concern(
        self,
        candidate_response: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        分析候选人的回复，判断真实顾虑

        Returns:
            dict: {
                "concern_type": "salary/growth/stability/team/other",
                "concern_level": "high/medium/low",
                "urgency": "high/medium/low",
                "analysis": "详细分析",
                "suggested_approach": "建议策略"
            }
        """
        user_prompt = f"""候选人回复: {candidate_response}

请分析候选人的真实顾虑和心理状态。

返回JSON格式：
{{
    "concern_type": "salary/growth/stability/team/other",
    "concern_level": "high/medium/low",
    "urgency": "high/medium/low",
    "analysis": "详细分析候选人的顾虑",
    "suggested_approach": "建议的应对策略"
}}"""

        response = await self.gateway.chat(
            prompt=user_prompt,
            system="你是一个专业的HR谈判分析师，擅长读懂候选人心理。",
            model="qwen3-omni",
        )

        try:
            json_str = self._extract_json(response.content)
            return json.loads(json_str)
        except:
            return {
                "concern_type": "unknown",
                "concern_level": "medium",
                "urgency": "medium",
                "analysis": candidate_response,
                "suggested_approach": "继续沟通",
            }

    async def suggest_counter_offer(
        self,
        current_offer: Dict[str, Any],
        candidate_expectation: Dict[str, Any],
        gap_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        基于LLM分析，建议下一个还价方案

        Returns:
            dict: 建议的方案，包含调整理由
        """
        user_prompt = f"""当前Offer: {self._format_offer(current_offer)}
候选人期望: {self._format_offer(candidate_expectation)}

差距分析: {gap_analysis.get('summary', '')}

请建议一个创意性的补偿方案，既能满足候选人主要诉求，又能控制公司成本。

返回JSON格式：
{{
    "proposed_salary": 月薪数字,
    "proposed_signing_bonus": 签字费数字,
    "proposed_rsu": RSU数量,
    "additional_benefits": ["额外福利列表"],
    "reasoning": "调整理由说明",
    "expected_acceptance_rate": "预计接受概率",
    "key_selling_points": ["主要卖点列表"]
}}"""

        response = await self.gateway.chat(
            prompt=user_prompt,
            system="你是一个薪酬谈判专家，擅长设计双赢方案。",
            model="qwen3-omni",
        )

        try:
            json_str = self._extract_json(response.content)
            return json.loads(json_str)
        except:
            return {
                "proposed_salary": current_offer.get("salary", 0),
                "reasoning": "使用当前方案",
            }

    def _format_offer(self, offer: Dict[str, Any]) -> str:
        """格式化Offer为文本"""
        lines = []
        if offer.get("salary"):
            lines.append(f"- 月薪: ¥{offer['salary']:,}")
        if offer.get("signing_bonus"):
            lines.append(f"- 签字费: ¥{offer['signing_bonus']:,}")
        if offer.get("rsu"):
            lines.append(f"- RSU: {offer['rsu']:,}股")
        if offer.get("vacation_days"):
            lines.append(f"- 年假: {offer['vacation_days']}天")
        if offer.get("remote_days"):
            lines.append(f"- 远程: 每周{offer['remote_days']}天")
        return "\n".join(lines) if lines else "未提供详细信息"

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
