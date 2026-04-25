"""
Negotiation Engine - Core Module
================================
Shared negotiation engine for Recruiter Agent and Candidate Agent.

Usage:
    from skills.negotiation import NegotiationEngine

    engine = NegotiationEngine(
        perspective='recruiter',  # or 'candidate'
        company_offer={...},
        candidate_expectation={...}
    )

    result = engine.analyze_and_negotiate(
        round_num=1,
        counter_offer=None  # or {'salary': 48000}
    )
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

from .strategies import (
    NegotiationStrategyLibrary,
    StrategyType,
    StrategyConfig,
)
from .prompts import PromptBuilder, ChannelType


@dataclass
class OfferComponents:
    """Offer各组成部分"""
    salary: int           # 月薪
    signing_bonus: int    # 签字费
    rsu: int              # 股票数量
    vesting_years: int     # 归属年限
    vacation_days: int     # 年假天数
    remote_days: int       # 每周远程天数
    learning_budget: int   # 年度学习基金
    other: List[str]       # 其他福利

    def total_first_year(self) -> int:
        """计算第一年总收入"""
        return (
            self.salary * 12 +
            self.signing_bonus +
            self.rsu * 100 * 0.25  # 假设第一年归属25%
        )

    def to_dict(self) -> dict:
        return {
            'salary': self.salary,
            'signing_bonus': self.signing_bonus,
            'rsu': self.rsu,
            'vesting_years': self.vesting_years,
            'vacation_days': self.vacation_days,
            'remote_days': self.remote_days,
            'learning_budget': self.learning_budget,
            'other': self.other,
        }


@dataclass
class GapAnalysis:
    """差距分析结果"""
    salary_gap: int
    salary_gap_pct: float
    total_package_gap: int
    total_package_gap_pct: float

    company_leverage: str  # 'company' / 'candidate' / 'balanced'
    urgency_level: str      # 'high' / 'normal' / 'low'

    summary: str


@dataclass
class NegotiationProposal:
    """谈判方案"""
    id: str
    title: str
    description: str
    components: OfferComponents
    highlights: List[str]
    recommended: bool
    strategy_type: StrategyType
    compromise_level: str  # 'high' / 'medium' / 'low'


@dataclass
class PersuasionResult:
    """说服结果"""
    headline: str
    talking_points: List[str]
    urgency_signals: List[str]
    risks: List[str]


@dataclass
class ChannelMessage:
    """渠道消息"""
    channel: ChannelType
    subject: Optional[str]
    body: str
    status: str  # 'pending' / 'sent' / 'delivered' / 'read' / 'replied'
    sent_at: Optional[datetime] = None


class NegotiationEngine:
    """
    谈判引擎 - Recruiter Agent和Candidate Agent共享
    """

    # 谈判成功的阈值
    MUTUAL_MATCH_THRESHOLD = 0.70  # 双方都达到70%以上即认为匹配
    COMPANY_MIN_THRESHOLD = 0.75    # 公司对候选人最低要求
    CANDIDATE_MIN_THRESHOLD = 0.70  # 候选人对公司最低要求

    def __init__(
        self,
        perspective: str,
        company_offer: dict,
        candidate_expectation: dict,
        job_context: Optional[dict] = None,
    ):
        """
        初始化谈判引擎

        Args:
            perspective: 'recruiter' 或 'candidate'
            company_offer: 公司Offer数据
            candidate_expectation: 候选人期望数据
            job_context: 职位上下文（可选）
        """
        self.perspective = perspective  # 'recruiter' or 'candidate'
        self.company_offer = self._normalize_offer(company_offer)
        self.candidate_expectation = self._normalize_expectation(candidate_expectation)
        self.job_context = job_context or {}
        self.strategy_library = NegotiationStrategyLibrary()
        self.prompt_builder = PromptBuilder()

        # 内部状态
        self._current_round = 0
        self._history: List[Dict[str, Any]] = []
        self._current_proposals: List[NegotiationProposal] = []
        self._deal_reached = False

    def _normalize_offer(self, offer: dict) -> OfferComponents:
        """标准化公司Offer"""
        return OfferComponents(
            salary=offer.get('salary', 0),
            signing_bonus=offer.get('signing_bonus', 0),
            rsu=offer.get('rsu', 0),
            vesting_years=offer.get('vesting_years', 4),
            vacation_days=offer.get('vacation_days', 10),
            remote_days=offer.get('remote_days', 1),
            learning_budget=offer.get('learning_budget', 0),
            other=offer.get('other', []),
        )

    def _normalize_expectation(self, exp: dict) -> OfferComponents:
        """标准化候选人期望"""
        return OfferComponents(
            salary=exp.get('salary', 0),
            signing_bonus=exp.get('signing_bonus', 0),
            rsu=exp.get('rsu', 0),
            vesting_years=exp.get('vesting_years', 4),
            vacation_days=exp.get('vacation_days', 15),
            remote_days=exp.get('remote_days', 2),
            learning_budget=exp.get('learning_budget', 5000),
            other=exp.get('other', []),
        )

    def analyze_gap(self) -> GapAnalysis:
        """
        分析双方差距
        """
        salary_gap = self.candidate_expectation.salary - self.company_offer.salary
        salary_gap_pct = salary_gap / self.company_offer.salary if self.company_offer.salary > 0 else 0

        total_package_gap = (
            self.candidate_expectation.total_first_year() -
            self.company_offer.total_first_year()
        )
        total_package_gap_pct = (
            total_package_gap / self.company_offer.total_first_year()
            if self.company_offer.total_first_year() > 0 else 0
        )

        # 判断谁占主导
        if salary_gap_pct > 0.05:
            leverage = 'candidate'  # 候选人期望偏高
        elif salary_gap_pct < -0.05:
            leverage = 'company'     # 公司Offer偏高
        else:
            leverage = 'balanced'

        # 判断紧迫度
        urgency = self.job_context.get('hiring_urgency', 'normal')
        market_competition = self.job_context.get('market_competition', 'medium')

        if urgency == 'high' or market_competition == 'fierce':
            urgency_level = 'high'
        elif urgency == 'low' and market_competition == 'low':
            urgency_level = 'low'
        else:
            urgency_level = 'normal'

        # 生成总结
        if leverage == 'candidate':
            summary = (
                f"候选人期望月薪比公司Offer高{salary_gap_pct*100:.0f}%，"
                f"差距约¥{salary_gap:,}。{urgency_level}紧迫度。"
            )
        elif leverage == 'company':
            summary = (
                f"候选人期望低于公司Offer，公司在谈判中占优势。"
            )
        else:
            summary = "双方预期接近，适合采用平衡策略。"

        return GapAnalysis(
            salary_gap=salary_gap,
            salary_gap_pct=salury_gap_pct,
            total_package_gap=total_package_gap,
            total_package_gap_pct=total_package_gap_pct,
            company_leverage=leverage,
            urgency_level=urgency_level,
            summary=summary,
        )

    def generate_proposals(self) -> List[NegotiationProposal]:
        """
        生成谈判方案列表
        """
        gap = self.analyze_gap()

        # 确定策略类型
        strategy_type = self.strategy_library.recommend_best(
            {
                'salary': self.company_offer.salary,
                'offer_percentile': self.job_context.get('offer_percentile', 50),
                'hiring_urgency': gap.urgency_level,
            },
            {
                'salary': self.candidate_expectation.salary,
                'market_percentile': self.job_context.get('candidate_market_percentile', 60),
                'needs_job_urgently': self.job_context.get('candidate_needs_job_urgently', False),
            }
        )

        # 获取对应策略
        strategies = self.strategy_library.get_strategies(strategy_type)

        proposals = []
        for i, config in enumerate(strategies):
            proposal = self._build_proposal(config, i)
            proposals.append(proposal)

        self._current_proposals = proposals
        return proposals

    def _build_proposal(self, config: StrategyConfig, index: int) -> NegotiationProposal:
        """根据策略配置构建方案"""
        # 计算调整后的薪资
        adjustment = config.salary_adjustment
        new_salary = int(self.company_offer.salary * (1 + adjustment))

        # 构建组件
        components = OfferComponents(
            salary=max(new_salary, self.candidate_expectation.salary * 0.9),
            signing_bonus=self._calculate_signing_bonus(adjustment),
            rsu=self._calculate_rsu(adjustment),
            vesting_years=4,
            vacation_days=self._calculate_vacation(config),
            remote_days=self._calculate_remote(config),
            learning_budget=self._calculate_learning_budget(config),
            other=[],
        )

        # 生成亮点
        highlights = self._generate_highlights(components, config)

        return NegotiationProposal(
            id=f"PROPOSAL_{index+1}",
            title=config.label,
            description=config.description,
            components=components,
            highlights=highlights,
            recommended=config.recommended,
            strategy_type=config.strategy_type,
            compromise_level='high' if config.recommended else 'low',
        )

    def _calculate_signing_bonus(self, adjustment: float) -> int:
        """计算签字费"""
        base = self.company_offer.signing_bonus
        if adjustment > 0:
            return int(base * (1 + abs(adjustment) * 2))
        return base

    def _calculate_rsu(self, adjustment: float) -> int:
        """计算RSU"""
        base = self.company_offer.rsu
        if adjustment > 0:
            return int(base * (1 + abs(adjustment)))
        return max(int(base * 0.8), 3000)

    def _calculate_vacation(self, config: StrategyConfig) -> int:
        """计算年假"""
        if '年假' in str(config.key_selling_points):
            return 15
        return max(self.company_offer.vacation_days, 12)

    def _calculate_remote(self, config: StrategyConfig) -> int:
        """计算远程工作天数"""
        if '远程' in str(config.key_selling_points):
            return 2
        return self.company_offer.remote_days

    def _calculate_learning_budget(self, config: StrategyConfig) -> int:
        """计算学习基金"""
        if '学习' in str(config.key_selling_points):
            return 15000
        return self.company_offer.learning_budget

    def _generate_highlights(self, components: OfferComponents, config: StrategyConfig) -> List[str]:
        """生成方案亮点"""
        highlights = []

        for point in config.key_selling_points:
            highlights.append(point)

        # 根据组件自动生成亮点
        if components.signing_bonus > self.company_offer.signing_bonus * 1.2:
            highlights.append(f"签字费高达¥{components.signing_bonus:,}，入职即兑现")

        if components.vacation_days > self.company_offer.vacation_days:
            highlights.append(f"年假{components.vacation_days}天，工作生活平衡")

        if components.remote_days > self.company_offer.remote_days:
            highlights.append(f"每周{components.remote_days}天远程工作")

        if components.learning_budget > 0:
            highlights.append(f"年度学习预算¥{components.learning_budget:,}")

        if components.rsu > self.company_offer.rsu:
            highlights.append(f"RSU {components.rsu:,}股，长期激励")

        return highlights[:4]  # 最多4个亮点

    def evaluate_mutual_fit(self) -> Dict[str, Any]:
        """
        评估双向匹配度
        """
        company_score = self._evaluate_from_company_perspective()
        candidate_score = self._evaluate_from_candidate_perspective()

        # 几何平均作为双向匹配度
        if company_score > 0 and candidate_score > 0:
            mutual_fit = (company_score * candidate_score) ** 0.5
        else:
            mutual_fit = min(company_score, candidate_score)

        mutual_reached = (
            company_score >= self.COMPANY_MIN_THRESHOLD and
            candidate_score >= self.CANDIDATE_MIN_THRESHOLD
        )

        return {
            'company_score': company_score,
            'candidate_score': candidate_score,
            'mutual_fit': mutual_fit,
            'mutual_reached': mutual_reached,
            'recommendation': self._get_recommendation(company_score, candidate_score),
        }

    def _evaluate_from_company_perspective(self) -> float:
        """从公司视角评估候选人"""
        score = 0.0
        weights = {
            'technical': 0.30,
            'experience': 0.25,
            'salary_fit': 0.20,
            'culture': 0.15,
            'potential': 0.10,
        }

        # 技术匹配
        required_skills = set(self.job_context.get('required_skills', []))
        candidate_skills = set(self.job_context.get('candidate_skills', []))
        if required_skills:
            skill_match = len(required_skills & candidate_skills) / len(required_skills)
            score += skill_match * weights['technical']

        # 经验匹配
        required_exp = self.job_context.get('required_years', 3)
        candidate_exp = self.job_context.get('candidate_years', 3)
        exp_ratio = min(candidate_exp / required_exp, 1.5)
        score += min(exp_ratio, 1.0) * weights['experience']

        # 薪资匹配度
        salary_ratio = self.company_offer.salary / max(self.candidate_expectation.salary, 1)
        score += min(salary_ratio, 1.0) * weights['salary_fit']

        # 文化匹配和潜力使用默认值
        score += 0.85 * weights['culture']
        score += 0.80 * weights['potential']

        return min(score, 1.0)

    def _evaluate_from_candidate_perspective(self) -> float:
        """从候选人视角评估公司"""
        score = 0.0
        weights = {
            'salary': 0.30,
            'growth': 0.25,
            'tech_stack': 0.20,
            'culture': 0.15,
            'balance': 0.10,
        }

        # 薪资满足度
        salary_ratio = self.company_offer.salary / max(self.candidate_expectation.salary, 1)
        score += min(salary_ratio, 1.0) * weights['salary']

        # 成长空间
        growth_score = self.job_context.get('growth_score', 0.80)
        score += growth_score * weights['growth']

        # 技术栈匹配度
        tech_match = self.job_context.get('tech_stack_match', 0.85)
        score += tech_match * weights['tech_stack']

        # 文化和平衡
        score += 0.80 * weights['culture']
        score += 0.75 * weights['balance']

        return min(score, 1.0)

    def _get_recommendation(self, company_score: float, candidate_score: float) -> str:
        """获取推荐结论"""
        if company_score >= 0.85 and candidate_score >= 0.85:
            return "强烈推荐：双向达标，优先发放Offer"
        elif company_score >= 0.75 and candidate_score >= 0.75:
            return "推荐：有调整空间，可开始谈判"
        elif company_score >= 0.65:
            return "可考虑：候选人优秀，但薪资差距需弥合"
        else:
            return "谨慎：存在较大不匹配，建议继续寻找"

    def generate_persuasion_for_recruiter(self) -> PersuasionResult:
        """
        生成说服公司方的内部建议（仅公司内部可见）
        """
        gap = self.analyze_gap()
        mutual = self.evaluate_mutual_fit()

        if gap.company_leverage == 'candidate':
            # 候选人占主导，说服公司让步
            headline = "候选人优秀，值得争取；适当让步优于错过人才"

            talking_points = [
                f"候选人评估得分{mutual['company_score']*100:.0f}%，属于top15%人才",
                f"市场同类岗位招聘周期约45天，等待成本约¥{int(mutual['company_score'] * 50000):,}",
                f"候选人当前可能有{2 if mutual['candidate_score'] > 0.8 else 1}个其他offer在流程中",
                f"强员入职后预计团队产出提升{mutual['company_score']*25:.0f}%",
            ]

            urgency_signals = [
                "⚡ 候选人稀缺，时间窗口有限",
                "⚡ 竞争公司正在积极招聘同类人才",
            ] if mutual['candidate_score'] > 0.8 else []

            risks = [
                "让步可能引发内部薪酬不平衡",
                "需向管理层说明溢价理由",
            ]

        elif gap.company_leverage == 'company':
            # 公司占主导，说服候选人接受
            headline = "候选人意向积极，应以理性数据推动成交"

            talking_points = [
                f"候选人表达了对岗位的强烈兴趣（意向得分{mutual['candidate_score']*100:.0f}%）",
                f"当前Offer总包已是预算上限，再让步需特批",
                f"候选人同级别市场薪资约¥{int(self.company_offer.salary * 1.05):,}",
                f"3-6个月调薪窗口可作为后期激励",
            ]

            urgency_signals = [
                "⚡ 候选人正在对比其他机会",
            ] if mutual['candidate_score'] < 0.75 else []

            risks = [
                "候选人可能因为无法协商而放弃",
                "需要准备好应对僵局的后备方案",
            ]

        else:
            # 平衡状态
            headline = "双方接近达成，应积极推动成交"

            talking_points = [
                "双方预期差距在可接受范围内",
                "当前方案已体现最大诚意",
                "快速关门比优化细节更重要",
                "长期合作价值高于短期博弈",
            ]

            urgency_signals = []
            risks = ["继续谈判可能导致候选人疲劳"]

        return PersuasionResult(
            headline=headline,
            talking_points=talking_points,
            urgency_signals=urgency_signals,
            risks=risks,
        )

    def generate_persuasion_for_candidate(self) -> PersuasionResult:
        """
        生成说服候选人方的内部建议（候选人Agent内部可见）
        """
        gap = self.analyze_gap()
        mutual = self.evaluate_mutual_fit()

        if gap.company_leverage == 'candidate':
            # 候选人占主导，帮助候选人最大化利益
            headline = "你在谈判中占优势，但需注意边界"

            talking_points = [
                "当前有多个谈判筹码，可以争取更多",
                "签字费和前期现金比长期薪资更确定",
                "可以要求增加年假或远程工作作为补充",
                "但要注意：过高的期望可能失去这个机会",
            ]

            urgency_signals = []
            risks = [
                "过度强硬可能导致公司撤回Offer",
                "竞争对手可能更快关门",
            ]

        elif gap.company_leverage == 'company':
            # 公司占主导，帮助候选人理性决策
            headline = "当前Offer已具备竞争力，建议认真考虑"

            talking_points = [
                f"月薪¥{self.company_offer.salary:,}已超出市场{mutual['candidate_score']*20-10:.0f}%分位",
                f"签字费¥{self.company_offer.signing_bonus:,}相当于{mutual['candidate_score']*3:.0f}个月薪资保障",
                "团队技术氛围好，长期成长价值高",
                "入职后3-6个月可申请调薪评估",
            ]

            urgency_signals = [
                "⚡ 候选人竞争激烈，此机会可能不会等待太久",
            ]

            risks = [
                "错过当前Offer可能需要重新求职周期",
                "市场时机不确定",
            ]

        else:
            headline = "Offer已达预期，可考虑接受"

            talking_points = [
                "薪资和福利都符合你的期望",
                "公司平台和技术栈匹配你的需求",
                "当前方案已是最佳，综合价值最优",
            ]

            urgency_signals = []
            risks = []

        return PersuasionResult(
            headline=headline,
            talking_points=talking_points,
            urgency_signals=urgency_signals,
            risks=risks,
        )

    def generate_message(
        self,
        round_num: int,
        sentiment: str,
        channel: ChannelType = ChannelType.WECHAT,
        proposal_index: Optional[int] = None,
    ) -> ChannelMessage:
        """
        生成对外发送的消息

        Args:
            round_num: 谈判轮次
            sentiment: 对方回复的情感 ('positive', 'negative', 'question', 'comparison')
            channel: 发送渠道
            proposal_index: 使用的方案索引
        """
        self._current_round = round_num

        # 获取方案
        if proposal_index is not None and proposal_index < len(self._current_proposals):
            proposal = self._current_proposals[proposal_index]
        else:
            proposal = self._current_proposals[0] if self._current_proposals else None

        # 构建消息
        if channel == ChannelType.EMAIL:
            subject, body = self.prompt_builder.build_email(
                email_type='negotiation' if not self._deal_reached else 'agreement',
                candidate_name=self.job_context.get('candidate_name', '候选人'),
                proposal=proposal.to_dict() if proposal else None,
            )
            message_body = body
        else:
            message_body = self.prompt_builder.build_wechat_message(
                round_num=round_num,
                sentiment=sentiment,
                proposal=proposal.to_dict() if proposal else None,
            )
            subject = None

        # 人性化处理
        message_body = self.prompt_builder.humanize(message_body, channel)

        return ChannelMessage(
            channel=channel,
            subject=subject,
            body=message_body,
            status='pending',
        )

    def analyze_and_negotiate(
        self,
        round_num: int,
        counter_offer: Optional[dict] = None,
        candidate_sentiment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        主谈判方法：分析差距 + 生成方案 + 返回完整结果

        Returns:
            包含所有分析、方案、说服内容的完整字典
        """
        # 记录历史
        self._history.append({
            'round': round_num,
            'counter_offer': counter_offer,
            'sentiment': candidate_sentiment,
            'timestamp': datetime.now().isoformat(),
        })

        # 分析差距
        gap = self.analyze_gap()

        # 生成方案
        proposals = self.generate_proposals()

        # 评估双向匹配
        mutual_fit = self.evaluate_mutual_fit()

        # 生成说服内容（根据视角）
        if self.perspective == 'recruiter':
            persuasion = self.generate_persuasion_for_recruiter()
        else:
            persuasion = self.generate_persuasion_for_candidate()

        # 生成消息
        message = self.generate_message(
            round_num=round_num,
            sentiment=candidate_sentiment or 'neutral',
            proposal_index=0,
        )

        # 判断是否达成
        if mutual_fit['mutual_reached'] and round_num >= 2:
            self._deal_reached = True

        return {
            'gap': {
                'salary_gap': gap.salary_gap,
                'salary_gap_pct': gap.salary_gap_pct,
                'total_package_gap': gap.total_package_gap,
                'leverage': gap.company_leverage,
                'urgency': gap.urgency_level,
                'summary': gap.summary,
            },
            'proposals': [
                {
                    'id': p.id,
                    'title': p.title,
                    'description': p.description,
                    'components': p.components.to_dict(),
                    'highlights': p.highlights,
                    'recommended': p.recommended,
                }
                for p in proposals
            ],
            'mutual_fit': mutual_fit,
            'persuasion': {
                'headline': persuasion.headline,
                'talking_points': persuasion.talking_points,
                'urgency_signals': persuasion.urgency_signals,
                'risks': persuasion.risks,
            },
            'message': {
                'channel': message.channel.value,
                'subject': message.subject,
                'body': message.body,
            },
            'deal_reached': self._deal_reached,
            'round': round_num,
        }

    def get_channel_delivery_status(self, channel: ChannelType) -> str:
        """模拟渠道发送状态"""
        statuses = ['sent', 'delivered', 'read']
        return random.choice(statuses)
