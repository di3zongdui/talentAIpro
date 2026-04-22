"""
Deal Tracker - 招聘撮合跟踪系统

功能：
1. 全流程状态跟踪
2. 关键节点自动提醒
3. 撮合分趋势分析
4. 漏斗转化率统计
5. 顾问绩效看板
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid


class DealStatus(Enum):
    """Deal状态"""
    # 候选人侧
    CANDIDATE_VIEWING = "候选人查看中"
    CANDIDATE_INTERESTED = "候选人有意向"
    CANDIDATE_INTERVIEWING = "面试中"
    CANDIDATE_OFFER = "Offer阶段"
    CANDIDATE_SIGNED = "已签约"
    CANDIDATE_REJECTED = "候选人拒绝"
    CANDIDATE_WITHDRAWN = "候选人退出"

    # 客户侧
    CLIENT_REVIEWING = "客户审核中"
    CLIENT_INTERESTED = "客户有意向"
    CLIENT_INTERVIEWING = "客户面试中"
    CLIENT_OFFER = "客户Offer中"
    CLIENT_SIGNED = "客户已签"

    # 中止
    ON_HOLD = "暂停中"
    CLOSED_LOST = "已关闭-失败"
    CLOSED_WON = "已关闭-成功"


class PipelineStage(Enum):
    """漏斗阶段"""
    SOURCING = "线索"
    SCREENING = "筛选"
    INTERVIEWING = "面试"
    OFFER = "Offer"
    HIRED = "入职"
    CLOSED = "关闭"


@dataclass
class DealEvent:
    """Deal事件"""
    event_id: str
    deal_id: str
    event_type: str  # status_change/note/reminder/email_sent/email_opened/email_replied
    timestamp: datetime
    from_status: Optional[str]
    to_status: Optional[str]
    note: Optional[str]
    actor: str  # system/consultant/candidate/client


@dataclass
class FollowUpReminder:
    """跟进提醒"""
    reminder_id: str
    deal_id: str
    scheduled_at: datetime
    reminder_type: str  # follow_up/interview/offer/expire
    message: str
    is_sent: bool = False


@dataclass
class Deal:
    """招聘撮合Deal"""
    deal_id: str
    candidate_id: str
    candidate_name: str
    candidate_title: str
    job_id: str
    job_title: str
    client_name: str

    # 撮合信息
    match_score: float
    composite_score: float
    surprise_highlights: List[str]

    # 状态跟踪
    current_status: DealStatus
    pipeline_stage: PipelineStage
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    # 关键日期
    sent_at: Optional[datetime]
    interview_at: Optional[datetime]
    offer_at: Optional[datetime]

    # 顾问
    consultant: str

    # 事件记录
    events: List[DealEvent] = field(default_factory=list)
    reminders: List[FollowUpReminder] = field(default_factory=list)

    # 邮件追踪
    email_opened: bool = False
    email_replied: bool = False
    open_count: int = 0


class DealTracker:
    """
    Deal Tracker - 招聘撮合跟踪系统

    完整的Deal生命周期管理
    """

    def __init__(self):
        self.deals: Dict[str, Deal] = {}
        self.events: List[DealEvent] = []
        self.reminders: List[FollowUpReminder] = []

        # 状态转移规则
        self.STATUS_TRANSITIONS = {
            # 候选人侧转移
            DealStatus.CANDIDATE_VIEWING: [DealStatus.CANDIDATE_INTERESTED, DealStatus.CANDIDATE_REJECTED, DealStatus.ON_HOLD],
            DealStatus.CANDIDATE_INTERESTED: [DealStatus.CANDIDATE_INTERVIEWING, DealStatus.CANDIDATE_REJECTED, DealStatus.ON_HOLD],
            DealStatus.CANDIDATE_INTERVIEWING: [DealStatus.CANDIDATE_OFFER, DealStatus.CANDIDATE_REJECTED, DealStatus.CANDIDATE_WITHDRAWN],
            DealStatus.CANDIDATE_OFFER: [DealStatus.CANDIDATE_SIGNED, DealStatus.CANDIDATE_REJECTED],
            DealStatus.CANDIDATE_SIGNED: [DealStatus.CLOSED_WON],
            # 客户侧转移
            DealStatus.CLIENT_REVIEWING: [DealStatus.CLIENT_INTERESTED, DealStatus.CLOSED_LOST],
            DealStatus.CLIENT_INTERESTED: [DealStatus.CLIENT_INTERVIEWING, DealStatus.CLOSED_LOST],
            DealStatus.CLIENT_INTERVIEWING: [DealStatus.CLIENT_OFFER, DealStatus.CLOSED_LOST],
            DealStatus.CLIENT_OFFER: [DealStatus.CLIENT_SIGNED, DealStatus.CLOSED_LOST],
            DealStatus.CLIENT_SIGNED: [DealStatus.CLOSED_WON],
            # 中止
            DealStatus.ON_HOLD: [DealStatus.CANDIDATE_INTERESTED, DealStatus.CLOSED_LOST],
            DealStatus.CANDIDATE_REJECTED: [DealStatus.CLOSED_LOST],
            DealStatus.CANDIDATE_WITHDRAWN: [DealStatus.CLOSED_LOST],
            DealStatus.CLOSED_LOST: [],
            DealStatus.CLOSED_WON: [],
        }

        # 阶段映射
        self.STAGE_MAPPING = {
            DealStatus.CANDIDATE_VIEWING: PipelineStage.SCREENING,
            DealStatus.CANDIDATE_INTERESTED: PipelineStage.SCREENING,
            DealStatus.CANDIDATE_INTERVIEWING: PipelineStage.INTERVIEWING,
            DealStatus.CANDIDATE_OFFER: PipelineStage.OFFER,
            DealStatus.CANDIDATE_SIGNED: PipelineStage.HIRED,
            DealStatus.CANDIDATE_REJECTED: PipelineStage.CLOSED,
            DealStatus.CANDIDATE_WITHDRAWN: PipelineStage.CLOSED,
            DealStatus.CLIENT_REVIEWING: PipelineStage.SCREENING,
            DealStatus.CLIENT_INTERESTED: PipelineStage.SCREENING,
            DealStatus.CLIENT_INTERVIEWING: PipelineStage.INTERVIEWING,
            DealStatus.CLIENT_OFFER: PipelineStage.OFFER,
            DealStatus.CLIENT_SIGNED: PipelineStage.HIRED,
            DealStatus.ON_HOLD: PipelineStage.SCREENING,
            DealStatus.CLOSED_LOST: PipelineStage.CLOSED,
            DealStatus.CLOSED_WON: PipelineStage.HIRED,
        }

    def create_deal(
        self,
        candidate_id: str,
        candidate_name: str,
        candidate_title: str,
        job_id: str,
        job_title: str,
        client_name: str,
        match_score: float,
        composite_score: float,
        surprise_highlights: List[str],
        consultant: str = "system"
    ) -> Deal:
        """
        创建新Deal

        Returns:
            Deal: 创建的Deal对象
        """
        deal_id = f"DEAL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        deal = Deal(
            deal_id=deal_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            candidate_title=candidate_title,
            job_id=job_id,
            job_title=job_title,
            client_name=client_name,
            match_score=match_score,
            composite_score=composite_score,
            surprise_highlights=surprise_highlights,
            current_status=DealStatus.CANDIDATE_VIEWING,
            pipeline_stage=PipelineStage.SOURCING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            closed_at=None,
            sent_at=None,
            interview_at=None,
            offer_at=None,
            consultant=consultant,
            events=[],
            reminders=[]
        )

        # 记录创建事件
        event = DealEvent(
            event_id=f"E-{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            event_type="deal_created",
            timestamp=datetime.now(),
            from_status=None,
            to_status=DealStatus.CANDIDATE_VIEWING.value,
            note="Deal创建",
            actor=consultant
        )
        deal.events.append(event)
        self.events.append(event)

        self.deals[deal_id] = deal

        return deal

    def update_status(
        self,
        deal_id: str,
        new_status: DealStatus,
        note: Optional[str] = None,
        actor: str = "system"
    ) -> bool:
        """
        更新Deal状态

        Returns:
            bool: 是否更新成功
        """
        if deal_id not in self.deals:
            return False

        deal = self.deals[deal_id]
        old_status = deal.current_status

        # 检查状态转移是否合法
        allowed = self.STATUS_TRANSITIONS.get(old_status, [])
        if new_status not in allowed and new_status != old_status:
            # 如果是同一个状态（刷新），允许
            pass

        # 更新状态
        deal.current_status = new_status
        deal.pipeline_stage = self.STAGE_MAPPING.get(new_status, deal.pipeline_stage)
        deal.updated_at = datetime.now()

        # 更新关键日期
        if new_status == DealStatus.CANDIDATE_INTERESTED and not deal.sent_at:
            deal.sent_at = datetime.now()
        elif new_status == DealStatus.CANDIDATE_INTERVIEWING and not deal.interview_at:
            deal.interview_at = datetime.now()
        elif new_status == DealStatus.CANDIDATE_OFFER and not deal.offer_at:
            deal.offer_at = datetime.now()
        elif new_status in [DealStatus.CLOSED_WON, DealStatus.CLOSED_LOST]:
            deal.closed_at = datetime.now()

        # 记录事件
        event = DealEvent(
            event_id=f"E-{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            event_type="status_change",
            timestamp=datetime.now(),
            from_status=old_status.value,
            to_status=new_status.value,
            note=note,
            actor=actor
        )
        deal.events.append(event)
        self.events.append(event)

        return True

    def add_note(
        self,
        deal_id: str,
        note: str,
        actor: str = "system"
    ) -> bool:
        """添加备注"""
        if deal_id not in self.deals:
            return False

        deal = self.deals[deal_id]
        deal.updated_at = datetime.now()

        event = DealEvent(
            event_id=f"E-{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            event_type="note",
            timestamp=datetime.now(),
            from_status=None,
            to_status=None,
            note=note,
            actor=actor
        )
        deal.events.append(event)
        self.events.append(event)

        return True

    def track_email_opened(
        self,
        deal_id: str
    ) -> bool:
        """追踪邮件打开"""
        if deal_id not in self.deals:
            return False

        deal = self.deals[deal_id]
        deal.email_opened = True
        deal.open_count += 1
        deal.updated_at = datetime.now()

        event = DealEvent(
            event_id=f"E-{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            event_type="email_opened",
            timestamp=datetime.now(),
            from_status=None,
            to_status=None,
            note=f"邮件被打开（第{deal.open_count}次）",
            actor="system"
        )
        deal.events.append(event)
        self.events.append(event)

        return True

    def track_email_replied(
        self,
        deal_id: str
    ) -> bool:
        """追踪邮件回复"""
        if deal_id not in self.deals:
            return False

        deal = self.deals[deal_id]
        deal.email_replied = True
        deal.updated_at = datetime.now()

        # 自动更新状态为有意向
        if deal.current_status == DealStatus.CANDIDATE_VIEWING:
            self.update_status(deal_id, DealStatus.CANDIDATE_INTERESTED,
                             note="候选人回复了邮件", actor="system")

        event = DealEvent(
            event_id=f"E-{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            event_type="email_replied",
            timestamp=datetime.now(),
            from_status=None,
            to_status=None,
            note="候选人回复了邮件",
            actor="system"
        )
        deal.events.append(event)
        self.events.append(event)

        return True

    def create_reminder(
        self,
        deal_id: str,
        reminder_type: str,
        scheduled_at: datetime,
        message: str
    ) -> Optional[FollowUpReminder]:
        """创建跟进提醒"""
        if deal_id not in self.deals:
            return None

        reminder = FollowUpReminder(
            reminder_id=f"R-{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            scheduled_at=scheduled_at,
            reminder_type=reminder_type,
            message=message
        )

        self.deals[deal_id].reminders.append(reminder)
        self.reminders.append(reminder)

        return reminder

    def get_pending_reminders(self, before_date: Optional[datetime] = None) -> List[FollowUpReminder]:
        """获取待发送的提醒"""
        if before_date is None:
            before_date = datetime.now()

        return [
            r for r in self.reminders
            if not r.is_sent and r.scheduled_at <= before_date
        ]

    def get_deal_summary(self, deal_id: str) -> Dict[str, Any]:
        """获取Deal摘要"""
        if deal_id not in self.deals:
            return {}

        deal = self.deals[deal_id]

        # 计算时间指标
        days_in_pipeline = (datetime.now() - deal.created_at).days
        days_since_update = (datetime.now() - deal.updated_at).days

        return {
            "deal_id": deal.deal_id,
            "candidate_name": deal.candidate_name,
            "job_title": deal.job_title,
            "current_status": deal.current_status.value,
            "pipeline_stage": deal.pipeline_stage.value,
            "match_score": deal.match_score,
            "composite_score": deal.composite_score,
            "days_in_pipeline": days_in_pipeline,
            "days_since_update": days_since_update,
            "email_opened": deal.email_opened,
            "email_replied": deal.email_replied,
            "open_count": deal.open_count,
            "consultant": deal.consultant,
            "next_action": self._get_next_action(deal)
        }

    def _get_next_action(self, deal: Deal) -> str:
        """获取Deal的下一步行动建议"""
        status = deal.current_status

        if status == DealStatus.CANDIDATE_VIEWING:
            if deal.days_since_update >= 3:
                return "建议跟进：候选人尚未查看或回复"
            else:
                return "等待候选人查看"
        elif status == DealStatus.CANDIDATE_INTERESTED:
            return "建议：安排面试"
        elif status == DealStatus.CANDIDATE_INTERVIEWING:
            return "进行中：面试阶段"
        elif status == DealStatus.CANDIDATE_OFFER:
            return "关键时刻：等待候选人决策"
        elif status == DealStatus.ON_HOLD:
            return "暂停：需重新激活"
        elif status == DealStatus.CLOSED_WON:
            return "已成功入职"
        elif status == DealStatus.CLOSED_LOST:
            return "已关闭-失败"
        else:
            return "状态待更新"

    def get_pipeline_stats(self, consultant: Optional[str] = None) -> Dict[str, Any]:
        """
        获取漏斗统计数据

        Returns:
            Dict: 包含各阶段数量、转化率、入职率等
        """
        deals = self.deals.values()
        if consultant:
            deals = [d for d in deals if d.consultant == consultant]

        # 统计各阶段数量
        stage_counts = {}
        for stage in PipelineStage:
            stage_counts[stage.value] = len([d for d in deals if d.pipeline_stage == stage])

        # 计算转化率
        total = len(deals)
        closed = stage_counts.get(PipelineStage.CLOSED.value, 0)
        hired = stage_counts.get(PipelineStage.HIRED.value, 0)

        return {
            "total_deals": total,
            "stage_distribution": stage_counts,
            "conversion_rate": round((total - closed) / total * 100, 1) if total > 0 else 0,
            "hired_count": hired,
            "success_rate": round(hired / total * 100, 1) if total > 0 else 0,
            "avg_days_to_close": self._calculate_avg_days(deals)
        }

    def _calculate_avg_days(self, deals: List[Deal]) -> float:
        """计算平均关闭天数"""
        closed_deals = [d for d in deals if d.closed_at]
        if not closed_deals:
            return 0

        total_days = sum((d.closed_at - d.created_at).days for d in closed_deals)
        return round(total_days / len(closed_deals), 1)

    def get_stale_deals(self, days_threshold: int = 7) -> List[Deal]:
        """获取长期未更新的Deal"""
        threshold = datetime.now() - timedelta(days=days_threshold)
        return [
            d for d in self.deals.values()
            if d.updated_at < threshold
            and d.current_status not in [DealStatus.CLOSED_WON, DealStatus.CLOSED_LOST]
        ]


def demo():
    """演示Deal Tracker"""
    tracker = DealTracker()

    # 创建Deal
    print("=" * 60)
    print("Deal Tracker - 演示")
    print("=" * 60)

    deal = tracker.create_deal(
        candidate_id="CAND-001",
        candidate_name="Levi Li",
        candidate_title="HR总监",
        job_id="JOB-001",
        job_title="具身智能HR负责人",
        client_name="某具身智能公司",
        match_score=85.0,
        composite_score=78.0,
        surprise_highlights=["具身智能创业经验", "管理50人团队", "大厂P9背景"],
        consultant="George"
    )
    print(f"\n[Step 1] 创建Deal: {deal.deal_id}")
    print(f"  候选人：{deal.candidate_name}")
    print(f"  职位：{deal.job_title}")
    print(f"  撮合分：{deal.composite_score}")

    # 模拟邮件打开
    tracker.track_email_opened(deal.deal_id)
    print(f"\n[Step 2] 追踪邮件打开")
    print(f"  打开次数：{deal.open_count}")

    # 模拟候选人回复
    tracker.track_email_replied(deal.deal_id)
    print(f"\n[Step 3] 追踪邮件回复")
    print(f"  状态更新：{deal.current_status.value}")

    # 获取摘要
    summary = tracker.get_deal_summary(deal.deal_id)
    print(f"\n[Step 4] Deal摘要")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # 创建跟进提醒
    reminder = tracker.create_reminder(
        deal_id=deal.deal_id,
        reminder_type="follow_up",
        scheduled_at=datetime.now() + timedelta(hours=2),
        message="候选人已回复，建议24小时内安排电话沟通"
    )
    print(f"\n[Step 5] 创建跟进提醒")
    print(f"  提醒ID：{reminder.reminder_id}")
    print(f"  消息：{reminder.message}")

    # 漏斗统计
    stats = tracker.get_pipeline_stats()
    print(f"\n[Step 6] 漏斗统计")
    print(f"  总Deal数：{stats['total_deals']}")
    print(f"  阶段分布：{stats['stage_distribution']}")
    print(f"  转化率：{stats['conversion_rate']}%")


if __name__ == "__main__":
    demo()