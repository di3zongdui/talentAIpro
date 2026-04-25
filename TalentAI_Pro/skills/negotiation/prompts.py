"""
Negotiation Prompts Module
========================
Humanized messaging templates for WeChat, Email, and other channels.
These prompts are designed to NOT reveal AI identity.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import random


class ChannelType(Enum):
    """发送渠道"""
    WECHAT = "wechat"
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    IN_PERSON = "in_person"


@dataclass
class MessageTemplate:
    """消息模板"""
    channel: ChannelType
    subject: Optional[str]  # For email

    # 开场白
    opening: str

    # 正文（会传入实际数据）
    body_template: str

    # 结尾
    closing: str

    # 语气风格
    tone: str  # "warm", "professional", "casual"


class WeChatTemplates:
    """微信消息模板"""

    OPENING_CASUAL = [
        "你好",
        "Hi",
        "在吗",
        "方便吗",
    ]

    CLOSING_CASUAL = [
        "期待你的回复~",
        "有想法随时告诉我",
        "我们继续聊",
        "期待合作！",
        "等你的好消息",
    ]

    GREETING_BY_ROUND = {
        1: "收到了你对offer的反馈，非常理解你的想法。",
        2: "我又跟团队沟通了一下，有几个新的想法想跟你聊聊。",
        3: "关于你提到的点，我又仔细想了一下。",
        4: "我们来回推了好几轮，我帮你整理了一个最终方案。",
    }

    REACTION_TO_POSITIVE = [
        "太好了！",
        "太好了，我们来确认一下细节。",
        "很高兴你对这个方向感兴趣！",
    ]

    REACTION_TO_NEGATIVE = [
        "理解你的顾虑。",
        "我明白你的意思。",
        "完全理解。",
    ]

    REACTION_TO_QUESTION = [
        "好问题，我来帮你解答一下。",
        "这个问题很好，我来详细说说。",
        "这也是我接下来想跟你聊的。",
    ]

    REACTION_TO_COMPARISON = [
        "理解你在对比不同选项。",
        "确实每家都有自己的方案，我来帮你分析一下。",
    ]


class EmailTemplates:
    """邮件模板"""

    SUBJECTS = {
        'initial': "【TalentAI Pro】高级Python工程师Offer确认 - 李明",
        'negotiation': "【TalentAI Pro】关于薪资方案的一些想法 - 李明",
        'agreement': "【TalentAI Pro】Offer条款确认 - 李明",
        'deadline': "【TalentAI Pro】Offer有效期提醒 - 李明",
    }

    OPENING_PROFESSIONAL = "李明你好，"

    BODY_TEMPLATES = {
        'negotiation': """
跟团队深入沟通后，我们认为你确实是我们非常看重的人才。关于你提到的薪资期望，我想跟你分享一个综合方案。

这个方案不仅仅是月薪的调整，而是从整体薪酬包的角度来规划，希望能更好地平衡你的短期需求和长期发展。

方便的话，我们可以约个时间电话聊几分钟？
        """,

        'proposal': """
经过综合评估，我们为这个岗位制定了一个特别的薪酬方案：

【薪酬方案】
• 月薪：¥{salary:,}
• 签字费：¥{signing_bonus:,}（入职首月一次性发放）
• 股票：RSU {rsu:,}股（分{vesting_years}年归属）
• 年假：{vacation_days}天
• 远程：每周{vacation_days}天

【方案亮点】
{highlights}

这个方案是我们能提供的最优综合方案，希望能跟你达成一致。
        """,

        'agreement': """
很高兴我们达成一致！以下是确认的最终Offer条款：

【最终Offer】
• 月薪：¥{final_salary:,}
• 签字费：¥{final_signing:,}
• 入职日期：{start_date}
• 岗位：{job_title}

正式Offer邮件将在你确认后24小时内发出。期待成为同事！
        """,

        'deadline': """
想跟进一下之前发给你的Offer。目前我们已经确定了最终条款，这个Offer的有效期到{deadline}。

如果一切确认无误，我们可以启动正式的入职流程。
如果你有任何问题，随时联系我。
        """
    }


class PromptBuilder:
    """构建自然语言消息"""

    def __init__(self):
        self.wechat = WeChatTemplates()
        self.email = EmailTemplates()

    def build_wechat_message(
        self,
        round_num: int,
        sentiment: str,
        proposal: Optional[dict] = None,
        closing: Optional[str] = None,
    ) -> str:
        """构建微信消息"""
        parts = []

        # Opening
        if round_num == 1:
            parts.append(self.wechat.GREETING_BY_ROUND.get(1, "你好"))
        else:
            parts.append(self.wechat.GREETING_BY_ROUND.get(round_num, "关于上次聊的"))

        # React to candidate's sentiment
        if sentiment == 'positive':
            parts.append(random.choice(self.wechat.REACTION_TO_POSITIVE))
        elif sentiment == 'negative':
            parts.append(random.choice(self.wechat.REACTION_TO_NEGATIVE))
        elif sentiment == 'question':
            parts.append(random.choice(self.wechat.REACTION_TO_QUESTION))
        elif sentiment == 'comparison':
            parts.append(random.choice(self.wechat.REACTION_TO_COMPARISON))

        # Add proposal if provided
        if proposal:
            parts.append(self._format_proposal_wechat(proposal))

        # Closing
        if closing:
            parts.append(closing)
        else:
            parts.append(random.choice(self.wechat.CLOSING_CASUAL))

        return "\n\n".join(parts)

    def _format_proposal_wechat(self, proposal: dict) -> str:
        """格式化方案为微信风格"""
        lines = ["", "---", ""]

        if proposal.get('salary'):
            lines.append(f"月薪 ¥{proposal['salary']:,}")

        if proposal.get('signing_bonus'):
            lines.append(f"签字费 ¥{proposal['signing_bonus']:,}（入职发放）")

        if proposal.get('rsu'):
            years = proposal.get('vesting_years', 4)
            lines.append(f"RSU {proposal['rsu']:,}股（分{years}年归属）")

        if proposal.get('vacation_days'):
            lines.append(f"年假{proposal['vacation_days']}天")

        if proposal.get('remote_days'):
            lines.append(f"远程工作每周{proposal['remote_days']}天")

        highlights = proposal.get('highlights', [])
        if highlights:
            lines.append("")
            lines.append("亮点:")
            for h in highlights[:3]:
                lines.append(f"• {h}")

        lines.append("", "---")

        return "\n".join(lines)

    def build_email(
        self,
        email_type: str,
        candidate_name: str,
        proposal: Optional[dict] = None,
        **kwargs
    ) -> tuple[str, str]:
        """构建邮件（返回subject和body）"""
        subject = self.email.SUBJECTS.get(email_type, "").replace("李明", candidate_name)

        body = self.email.OPENING_PROFESSIONAL + "\n\n"

        if email_type == 'negotiation' and 'body_template' in self.email.BODY_TEMPLATES:
            body += self.email.BODY_TEMPLATES['negotiation']

        elif email_type == 'proposal' and proposal:
            template = self.email.BODY_TEMPLATES['proposal']
            # Format the template with proposal data
            highlights = "\n".join([f"• {h}" for h in proposal.get('highlights', [])[:4]])
            body += template.format(
                salary=proposal.get('salary', 0),
                signing_bonus=proposal.get('signing_bonus', 0),
                rsu=proposal.get('rsu', 0),
                vesting_years=proposal.get('vesting_years', 4),
                vacation_days=proposal.get('vacation_days', 15),
                remote_days=proposal.get('remote_days', 2),
                highlights=highlights,
            )

        elif email_type == 'agreement':
            template = self.email.BODY_TEMPLATES['agreement']
            body += template.format(
                final_salary=kwargs.get('final_salary', 0),
                final_signing=kwargs.get('final_signing', 0),
                start_date=kwargs.get('start_date', '待确认'),
                job_title=kwargs.get('job_title', '高级Python工程师'),
            )

        elif email_type == 'deadline':
            template = self.email.BODY_TEMPLATES['deadline']
            body += template.format(deadline=kwargs.get('deadline', '本周五'))

        body += "\n\n如有疑问，欢迎随时联系。\n\nBest regards,\nHR张老师"

        return subject, body

    def humanize(self, text: str, channel: ChannelType = ChannelType.WECHAT) -> str:
        """
        对消息进行人性化处理，确保不暴露AI身份
        """
        # 移除任何可能的AI标识
        text = text.replace("作为AI", "")
        text = text.replace("AI分析", "")
        text = text.replace("Agent", "")
        text = text.replace("系统", "我")
        text = text.replace("分析显示", "我了解")
        text = text.replace("数据表明", "从我观察到的情况看")

        # 微信风格调整
        if channel == ChannelType.WECHAT:
            text = text.replace("非常感谢", "太感谢了")
            text = text.replace("请查收", "")
            text = text.replace("此致", "")
            text = text.replace("敬礼", "")

        return text
