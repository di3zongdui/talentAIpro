"""
Negotiation Strategies Module
============================
Defines different negotiation strategies and their parameters.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class StrategyType(Enum):
    """谈判策略类型"""
    # 候选人主导时（公司需要让步）
    CANDIDATE_LEAD = "candidate_lead"

    # 公司主导时（候选人需要接受）
    COMPANY_LEAD = "company_lead"

    # 双方接近，寻求平衡
    BALANCED = "balanced"

    # 候选人特别优秀，值得高价争取
    PREMIUM = "premium"

    # 候选人急需工作，接受现有条件
    DISCOUNT = "discount"


@dataclass
class StrategyConfig:
    """策略配置"""
    strategy_type: StrategyType
    label: str
    description: str

    # 薪资调整比例 (正值=给候选人更多, 负值=给公司省更多)
    salary_adjustment: float  # e.g., 0.05 = 5% more for candidate

    # 是否推荐此策略
    recommended: bool

    # 核心卖点
    key_selling_points: List[str]

    # 适用场景
   适用场景: str

    # 风险提示
    risk_note: Optional[str] = None


class NegotiationStrategyLibrary:
    """策略库"""

    STRATEGIES = {
        StrategyType.CANDIDATE_LEAD: [
            StrategyConfig(
                strategy_type=StrategyType.CANDIDATE_LEAD,
                label="前端激励型",
                description="提高签字费和前期现金，降低长期固定成本",
                salary_adjustment=0.03,
                recommended=True,
                key_selling_points=[
                    "签字费高达¥40,000，入职即兑现",
                    "前期收入显著提升",
                    "后续绩效奖金可期",
                ],
                适用场景="候选人看重短期现金，不在乎长期股票归属",
            ),
            StrategyConfig(
                strategy_type=StrategyType.CANDIDATE_LEAD,
                label="综合福利型",
                description="用年假/远程工作/学习基金替代部分现金",
                salary_adjustment=0.02,
                recommended=True,
                key_selling_points=[
                    "年假从10天增至15天",
                    "每周2天远程工作",
                    "年度学习预算¥15,000",
                ],
                适用场景="候选人重视工作生活平衡和个人成长",
            ),
            StrategyConfig(
                strategy_type=StrategyType.CANDIDATE_LEAD,
                label="个性化定制",
                description="根据候选人具体诉求定制福利包",
                salary_adjustment=0.015,
                recommended=False,
                key_selling_points=[
                    "完全按需定制",
                    "灵活调整",
                    "体现诚意",
                ],
                适用场景="候选人有明确的非现金诉求",
                risk_note="执行复杂度高，需HR跟进",
            ),
        ],

        StrategyType.COMPANY_LEAD: [
            StrategyConfig(
                strategy_type=StrategyType.COMPANY_LEAD,
                label="绩效导向型",
                description="基础薪资维持上限，绩效奖金上浮",
                salary_adjustment=-0.02,
                recommended=True,
                key_selling_points=[
                    "绩效奖金上浮20%",
                    "与公司业绩挂钩",
                    "高产出高回报",
                ],
                适用场景="候选人有信心产出高绩效",
            ),
            StrategyConfig(
                strategy_type=StrategyType.COMPANY_LEAD,
                label="阶梯调薪型",
                description="3-6个月后逐步达到期望薪资",
                salary_adjustment=0.0,
                recommended=True,
                key_selling_points=[
                    "入职¥42,000",
                    "3个月后评估调薪",
                    "6个月后可达¥45,000",
                ],
                适用场景="候选人愿意等待，认可后期价值",
                risk_note="需明确的调薪标准和书面承诺",
            ),
            StrategyConfig(
                strategy_type=StrategyType.COMPANY_LEAD,
                label="市场数据型",
                description="用市场薪资数据证明offer合理性",
                salary_adjustment=-0.03,
                recommended=False,
                key_selling_points=[
                    "市场同级别中位¥42,000",
                    "你已超出市场25%分位",
                    "长期成长价值更高",
                ],
                适用场景="候选人对市场数据敏感",
                risk_note="可能显得冷淡，缺乏人情味",
            ),
        ],

        StrategyType.BALANCED: [
            StrategyConfig(
                strategy_type=StrategyType.BALANCED,
                label="各让一步",
                description="双方各承担50%差距，公平合理",
                salary_adjustment=0.0,
                recommended=True,
                key_selling_points=[
                    "各让50%达成一致",
                    "公平合理",
                    "长期合作基础",
                ],
                适用场景="双方差距不大，愿意各退一步",
            ),
        ],

        StrategyType.PREMIUM: [
            StrategyConfig(
                strategy_type=StrategyType.PREMIUM,
                label="明星人才溢价",
                description="超出预算争取顶尖人才",
                salary_adjustment=0.08,
                recommended=False,
                key_selling_points=[
                    "突破预算上限",
                    "市场溢价争取",
                    "快速到岗激励",
                ],
                适用场景="候选人极度稀缺，招聘周期紧迫",
                risk_note="可能引发内部薪酬不平衡",
            ),
        ],

        StrategyType.DISCOUNT: [
            StrategyConfig(
                strategy_type=StrategyType.DISCOUNT,
                label="快速入职折扣",
                description="接受候选人现有条件，快速关门",
                salary_adjustment=0.10,
                recommended=False,
                key_selling_points=[
                    "完全满足期望",
                    "立即入职",
                    "无谈判成本",
                ],
                适用场景="招聘紧迫，候选人为首选",
                risk_note="未充分利用谈判空间",
            ),
        ],
    }

    @classmethod
    def get_strategies(cls, strategy_type: StrategyType) -> List[StrategyConfig]:
        return cls.STRATEGIES.get(strategy_type, [])

    @classmethod
    def recommend_best(cls, company_offer: dict, candidate_expectation: dict) -> StrategyType:
        """根据双方条件推荐最佳策略类型"""
        salary_gap_pct = (candidate_expectation['salary'] - company_offer['salary']) / company_offer['salary']
        market_gap_pct = candidate_expectation['market_percentile'] - company_offer['offer_percentile']
        urgency = company_offer.get('hiring_urgency', 'normal')

        if salary_gap_pct <= 0.02 and market_gap_pct <= 5:
            return StrategyType.BALANCED
        elif salary_gap_pct > 0.08 or market_gap_pct > 15:
            if urgency == 'high':
                return StrategyType.PREMIUM
            return StrategyType.COMPANY_LEAD
        elif salary_gap_pct > 0.05 or market_gap_pct > 10:
            return StrategyType.CANDIDATE_LEAD
        elif candidate_expectation.get('needs_job_urgently'):
            return StrategyType.DISCOUNT
        else:
            return StrategyType.BALANCED
