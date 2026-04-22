"""
Smart Outreach Engine v2.0 - 智能触达邮件引擎

功能升级：
1. 超预期亮点自动注入（Discovery Radar发现 → 自动写入邮件）
2. 候选人语言风格适配
3. 邮件变体生成（简洁版/完整版/高管版）
4. 邮件效果追踪
5. 跟进时机建议
6. 拒绝话术库
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random


class EmailVariant(Enum):
    """邮件变体类型"""
    CONCISE = "简洁版"       # 短小精悍，快速浏览
    COMPLETE = "完整版"      # 详细全面，说明充分
    EXECUTIVE = "高管版"    # 高管风格，简洁权威


class CandidateStyle(Enum):
    """候选人语言风格"""
    TECHNICAL = "技术型"     # 强调技术、能力、数据
    COMMERCIAL = "商业型"   # 强调业务、价值、成果
    ACADEMIC = "学术型"     # 强调研究、创新、影响力
    GENERAL = "通用型"      # 平衡型风格


@dataclass
class SurpriseHighlight:
    """超预期亮点（从Discovery Radar或Candidate Intelligence获取）"""
    type: str           # github/paper/entrepreneurship/management/education
    highlight: str      # 亮点描述
    source: str         # 来源
    value_level: str    # 高/中/低


@dataclass
class EmailContent:
    """邮件内容"""
    subject: str
    body: str
    variant: EmailVariant
    style: CandidateStyle
    surprise_highlights_used: List[str]  # 使用的亮点列表


@dataclass
class OutreachResult:
    """触达结果"""
    email_id: str
    candidate_id: str
    job_id: str
    variant: EmailVariant
    sent_at: Optional[datetime]
    status: str  # draft/sent/delivered/opened/replied/rejected
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    open_count: int
    recommendation: str  # 发送建议


class SmartOutlookEngineV2:
    """
    Smart Outreach Engine v2.0

    在v1基础上增加：
    1. 超预期亮点自动注入
    2. 多变体生成
    3. 效果追踪
    """

    def __init__(self):
        # 风格适配规则
        self.STYLE_PATTERNS = {
            "technical": {
                "keywords": ["GitHub", "算法", "架构", "性能", "开源", "代码", "技术栈"],
                "tone": "专业、简洁、数据驱动",
                "focus": "技术能力、项目成果、技术影响力"
            },
            "commercial": {
                "keywords": ["增长", "营收", "商业化", "用户", "市场份额", "KPI"],
                "tone": "商业导向、价值驱动、结果导向",
                "focus": "业务成果、商业价值、团队贡献"
            },
            "academic": {
                "keywords": ["研究", "论文", "学术", "创新", "顶会", "算法"],
                "tone": "学术严谨、创新导向、影响力",
                "focus": "研究深度、创新能力、学术影响"
            },
            "general": {
                "keywords": [],
                "tone": "平衡、专业、友好",
                "focus": "综合能力、职业发展、团队契合"
            }
        }

        # 跟进时机建议
        self.FOLLOWUP_TIMING = {
            "linkedin_active": {
                "best_days": ["周二", "周三", "周四"],
                "best_hours": ["10:00-11:00", "14:00-15:00", "20:00-21:00"]
            },
            "general": {
                "best_days": ["周二", "周三", "周四"],
                "best_hours": ["09:00-10:00", "15:00-16:00"]
            }
        }

        # 拒绝话术库
        self.REJECTION_TEMPLATES = {
            "salary_mismatch": [
                "感谢您的时间。虽然目前这个机会在薪资层面可能不是最佳匹配，",
                "但我们仍然非常欣赏您的背景。如果未来有其他机会，欢迎保持联系。"
            ],
            "level_mismatch": [
                "感谢您的兴趣。基于对您经历的评估，",
                "我们认为可能有更合适的机会可以探讨。期待未来合作。"
            ],
            "timing": [
                "感谢您的回复。目前这个岗位正在积极推进中，",
                "期待很快能与您进一步沟通。祝好。"
            ]
        }

    def generate_email(
        self,
        candidate_name: str,
        candidate_title: str,
        company_name: str,
        job_title: str,
        job_highlights: List[str],  # JD的超预期亮点
        candidate_highlights: List[SurpriseHighlight],  # 候选人的超预期亮点
        candidate_style: CandidateStyle = CandidateStyle.GENERAL,
        variant: EmailVariant = EmailVariant.COMPLETE,
        is_referral: bool = False,
    ) -> EmailContent:
        """
        生成个性化邮件

        Args:
            candidate_name: 候选人姓名
            candidate_title: 候选人当前职位
            company_name: 候选人当前公司
            job_title: 目标职位
            job_highlights: JD/公司的超预期亮点
            candidate_highlights: 候选人的超预期亮点
            candidate_style: 候选人风格
            variant: 邮件变体
            is_referral: 是否是内推

        Returns:
            EmailContent: 邮件内容
        """
        # 1. 选择风格模板
        style_key = candidate_style.value if hasattr(candidate_style, 'value') else str(candidate_style)
        style_info = self.STYLE_PATTERNS.get(style_key.lower(), self.STYLE_PATTERNS["general"])

        # 2. 生成主题行
        subject = self._generate_subject(job_title, candidate_highlights, is_referral)

        # 3. 生成正文
        body = self._generate_body(
            candidate_name, candidate_title, company_name,
            job_title, job_highlights, candidate_highlights,
            style_info, variant, is_referral
        )

        return EmailContent(
            subject=subject,
            body=body,
            variant=variant,
            style=candidate_style,
            surprise_highlights_used=[h.highlight for h in candidate_highlights]
        )

    def _generate_subject(
        self,
        job_title: str,
        candidate_highlights: List[SurpriseHighlight],
        is_referral: bool
    ) -> str:
        """生成主题行"""
        prefix = "[内推] " if is_referral else ""

        # 从候选人亮点中选一个最强的
        top_highlight = None
        for h in candidate_highlights:
            if h.value_level == "高" and h.type in ["entrepreneurship", "management", "background"]:
                top_highlight = h.highlight
                break

        if top_highlight and len(candidate_highlights) >= 2:
            return f"{prefix}{job_title} - 您的{top_highlight}背景让我们特别感兴趣"
        else:
            return f"{prefix}{job_title} - CGL高端猎头推荐"

    def _generate_body(
        self,
        candidate_name: str,
        candidate_title: str,
        company_name: str,
        job_title: str,
        job_highlights: List[str],
        candidate_highlights: List[SurpriseHighlight],
        style_info: Dict,
        variant: EmailVariant,
        is_referral: bool
    ) -> str:
        """生成邮件正文"""
        style = style_info["tone"]

        # 开场白
        if is_referral:
            opening = f"{candidate_name}您好，"
        else:
            opening = f"尊敬的{candidate_name}，"

        # 候选人亮点段落（超预期亮点注入）
        highlight_paragraph = self._generate_highlight_paragraph(
            candidate_highlights, style_info, variant
        )

        # 职位亮点段落
        job_paragraph = self._generate_job_paragraph(job_title, job_highlights, style_info, variant)

        # 结尾
        closing = self._generate_closing(variant)

        # 组装邮件
        if variant == EmailVariant.CONCISE:
            body = f"""{opening}

我在寻找{candidate_title}方向的人才，您的背景让我印象深刻。

{highlight_paragraph[:100]}...

{job_paragraph[:100]}...

{closing}"""
        elif variant == EmailVariant.EXECUTIVE:
            body = f"""{opening}

贵司{candidate_title}的背景在行业内有口皆碑。

{highlight_paragraph}

我司正在寻找{job_title}，认为您的经历能够创造独特价值。

{job_paragraph[:150]}...

{closing}"""
        else:  # COMPLETE
            body = f"""{opening}

我是CGL高端猎头的George，专注于AI/科技领域的人才战略。

【为什么联系您】
{highlight_paragraph}

【关于这个机会】
{job_paragraph}

【我们可以提供】
• 具有竞争力的薪酬方案（基础薪资+股权激励）
• 具身智能赛道的高速增长机会
• 直接汇报给创始人/CEO的职位机会
• 团队搭建的从0到1经历

{closing}

祝好，
George Guo
CGL高端猎头
"""

        return body

    def _generate_highlight_paragraph(
        self,
        candidate_highlights: List[SurpriseHighlight],
        style_info: Dict,
        variant: EmailVariant
    ) -> str:
        """生成候选人亮点段落"""
        if not candidate_highlights:
            return "您的职业背景与我们正在寻找的人才画像高度匹配。"

        # 选择top亮点
        top_highlights = candidate_highlights[:3]

        paragraphs = []
        for h in top_highlights:
            if h.type == "entrepreneurship":
                paragraphs.append(f"✓ 创业实战：{h.highlight}，这是最具价值的经历之一")
            elif h.type == "management":
                paragraphs.append(f"✓ 团队管理：{h.highlight}，展现了卓越的组织能力")
            elif h.type == "background":
                paragraphs.append(f"✓ 行业背景：{h.highlight}，这是稀缺的行业洞察")
            elif h.type == "github":
                paragraphs.append(f"✓ 技术影响力：{h.highlight}，证明了您的技术实力")
            elif h.type == "paper":
                paragraphs.append(f"✓ 学术深度：{h.highlight}，体现了创新思维")
            else:
                paragraphs.append(f"✓ {h.highlight}")

        if variant == EmailVariant.CONCISE:
            return paragraphs[0] if paragraphs else ""

        return "\n".join(paragraphs)

    def _generate_job_paragraph(
        self,
        job_title: str,
        job_highlights: List[str],
        style_info: Dict,
        variant: EmailVariant
    ) -> str:
        """生成职位亮点段落"""
        focus = style_info["focus"]

        highlight_text = ""
        if job_highlights:
            top_job_highlights = job_highlights[:2]
            highlight_text = "、".join(top_job_highlights)

        base = f"""我司正在寻找{job_title}。

职位亮点：
• 赛道红利：具身智能是2026年最火热的投资方向
• 团队背景：创始团队来自顶级科技公司和投资机构
• 薪酬方案：具有市场竞争力的现金薪酬+股权激励"""

        if highlight_text:
            base += f"\n• 超预期价值：{highlight_text}"

        return base

    def _generate_closing(self, variant: EmailVariant) -> str:
        """生成结尾"""
        if variant == EmailVariant.CONCISE:
            return "期待您的回复。"
        elif variant == EmailVariant.EXECUTIVE:
            return "如感兴趣，请在24小时内回复，我将第一时间为您对接。"
        else:
            return """如果您对这个机会感兴趣，我非常愿意进一步详细沟通。
您可以在我的日历上预约时间：calendly.com/george-guo

即使暂时没有意向，也希望能保持联系。未来可能还有更适合的机会。"""

    def generate_variants(
        self,
        candidate_name: str,
        candidate_title: str,
        company_name: str,
        job_title: str,
        job_highlights: List[str],
        candidate_highlights: List[SurpriseHighlight],
        candidate_style: CandidateStyle = CandidateStyle.GENERAL
    ) -> List[EmailContent]:
        """
        生成3种变体邮件

        Returns:
            List[EmailContent]: [简洁版, 完整版, 高管版]
        """
        variants = [
            EmailVariant.CONCISE,
            EmailVariant.COMPLETE,
            EmailVariant.EXECUTIVE
        ]

        return [
            self.generate_email(
                candidate_name, candidate_title, company_name,
                job_title, job_highlights, candidate_highlights,
                candidate_style, v
            )
            for v in variants
        ]

    def get_followup_timing(
        self,
        candidate_linkedin_active: bool = False,
        last_contact_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取跟进时机建议

        Args:
            candidate_linkedin_active: 候选人LinkedIn是否活跃
            last_contact_date: 上次联系时间

        Returns:
            Dict: 包含最佳联系时间、跟进建议
        """
        timing_key = "linkedin_active" if candidate_linkedin_active else "general"
        timing = self.FOLLOWUP_TIMING[timing_key]

        # 如果有上次联系时间，计算下次最佳联系时间
        next_best = None
        followup_suggestion = ""

        if last_contact_date:
            days_since = (datetime.now() - last_contact_date).days
            if days_since < 3:
                followup_suggestion = "刚联系过，建议3-5天后再跟进"
            elif days_since < 7:
                followup_suggestion = "是时候跟进了，建议今天联系"
            else:
                followup_suggestion = "已经超过1周，建议尽快跟进"

            next_best = last_contact_date + timedelta(days=5)
        else:
            followup_suggestion = "首次联系建议在周二-周四进行"

        return {
            "best_days": timing["best_days"],
            "best_hours": timing["best_hours"],
            "followup_suggestion": followup_suggestion,
            "next_best_date": next_best
        }

    def get_rejection_message(
        self,
        reason: str,
        candidate_name: str,
        keep_connection: bool = True
    ) -> str:
        """
        生成拒绝话术（留人口碑）

        Args:
            reason: 拒绝原因
            candidate_name: 候选人姓名
            keep_connection: 是否保持联系

        Returns:
            str: 拒绝邮件内容
        """
        template = self.REJECTION_TEMPLATES.get(reason, self.REJECTION_TEMPLATES["timing"])

        body = f"尊敬的{candidate_name}，\n\n"
        body += template[0]
        if keep_connection:
            body += "我们珍视这次交流的机会，期待未来有其他合作可能。"
        body += "\n\n" + template[1]
        body += "\n\n祝好，\nGeorge Guo\nCGL高端猎头"

        return body

    def track_email_result(
        self,
        email_id: str,
        candidate_id: str,
        job_id: str,
        variant: EmailVariant
    ) -> OutreachResult:
        """
        创建邮件追踪记录

        Returns:
            OutreachResult: 追踪结果对象
        """
        return OutreachResult(
            email_id=email_id,
            candidate_id=candidate_id,
            job_id=job_id,
            variant=variant,
            sent_at=None,
            status="draft",
            opened_at=None,
            replied_at=None,
            open_count=0,
            recommendation=self._get_send_recommendation(variant)
        )

    def _get_send_recommendation(self, variant: EmailVariant) -> str:
        """获取发送建议"""
        recommendations = {
            EmailVariant.CONCISE: "适合快速浏览场景，建议作为第一封邮件使用",
            EmailVariant.COMPLETE: "信息全面，适合对职位有一定了解的候选人",
            EmailVariant.EXECUTIVE: "适合高端候选人，建议配合电话跟进"
        }
        return recommendations.get(variant, "")


def demo():
    """演示Smart Outreach Engine v2.0"""
    engine = SmartOutlookEngineV2()

    # 模拟候选人超预期亮点
    candidate_highlights = [
        SurpriseHighlight(
            type="entrepreneurship",
            highlight="具身智能创业经历（与JD方向完全match）",
            source="Candidate Intelligence",
            value_level="高"
        ),
        SurpriseHighlight(
            type="management",
            highlight="管理50人团队（超出JD要求）",
            source="Resume解析",
            value_level="高"
        ),
        SurpriseHighlight(
            type="background",
            highlight="大厂P9背景（稀缺资源）",
            source="Discovery Radar",
            value_level="中"
        )
    ]

    # 模拟JD超预期亮点
    job_highlights = [
        "2026年Q1融资200亿，赛道最热方向",
        "创始团队来自斯坦福/清华，背景豪华"
    ]

    print("=" * 60)
    print("Smart Outreach Engine v2.0 - 演示")
    print("=" * 60)

    # 生成3种变体
    print("\n【生成3种邮件变体】")
    variants = engine.generate_variants(
        candidate_name="Levi Li",
        candidate_title="HR总监",
        company_name="某具身智能创业公司",
        job_title="具身智能HR负责人",
        job_highlights=job_highlights,
        candidate_highlights=candidate_highlights
    )

    for email in variants:
        print(f"\n--- {email.variant.value} ---")
        print(f"主题：{email.subject}")
        print(f"正文预览：{email.body[:200]}...")

    # 跟进时机
    print("\n\n【跟进时机建议】")
    timing = engine.get_followup_timing(candidate_linkedin_active=True)
    print(f"最佳日期：{', '.join(timing['best_days'])}")
    print(f"最佳时段：{', '.join(timing['best_hours'])}")
    print(f"建议：{timing['followup_suggestion']}")

    # 拒绝话术
    print("\n\n【拒绝话术示例】")
    rejection = engine.get_rejection_message("salary_mismatch", "张三", keep_connection=True)
    print(rejection)


if __name__ == "__main__":
    demo()