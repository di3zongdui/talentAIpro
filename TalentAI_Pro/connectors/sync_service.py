# -*- coding: utf-8 -*-
"""
数据同步服务 - TalentAI Pro
功能: 将飞书/Bitable数据同步到TalentAI Pro内部模型
"""

import json
import time
import sys
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from skills.jd_parser.jd_intelligence_v2 import JDIntelligenceEngine
    from skills.resume_parser.candidate_intelligence_v2 import CandidateIntelligenceEngine
    from skills.discovery_radar.discovery_radar import DiscoveryRadar
    from skills.smart_outreach.smart_outreach_engine_v2 import SmartOutreachEngine
    from skills.deal_tracker.deal_tracker import Deal, DealStage, DealTracker
    from engine.matching_v2 import MatchingEngineV2
except ImportError:
    # 尝试相对导入
    try:
        from ..skills.jd_parser.jd_intelligence_v2 import JDIntelligenceEngine
        from ..skills.resume_parser.candidate_intelligence_v2 import CandidateIntelligenceEngine
        from ..skills.discovery_radar.discovery_radar import DiscoveryRadar
        from ..skills.smart_outreach.smart_outreach_engine_v2 import SmartOutreachEngine
        from ..skills.deal_tracker.deal_tracker import Deal, DealStage, DealTracker
        from ..engine.matching_v2 import MatchingEngineV2
    except ImportError:
        # Mock导入用于测试
        JDIntelligenceEngine = None
        CandidateIntelligenceEngine = None
        DiscoveryRadar = None
        SmartOutreachEngine = None
        Deal = None
        DealTracker = None
        MatchingEngineV2 = None
        # 定义Mock DealStage
        class MockDealStage(Enum):
            SOURCED = "sourced"
            CONTACTED = "contacted"
            SCREENING = "screening"
            INTERVIEWING = "interviewing"
            OFFER = "offer"
            HIRED = "hired"
            REJECTED = "rejected"
            WITHDRAWN = "withdrawn"
        DealStage = MockDealStage


class SyncStatus(Enum):
    """同步状态"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    NO_DATA = "no_data"


@dataclass
class SyncResult:
    """同步结果"""
    status: SyncStatus
    synced_count: int = 0
    failed_count: int = 0
    errors: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConfig:
    """同步配置"""
    # 飞书配置
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_tenant_token: str = ""

    # Bitable配置
    bitable_app_token: str = ""
    bitable_encryption_key: str = ""

    # 同步选项
    sync_candidates: bool = True
    sync_jobs: bool = True
    sync_deals: bool = True
    sync_calendar: bool = False

    # 智能处理
    run_jd_intelligence: bool = True
    run_candidate_intelligence: bool = True
    run_discovery_radar: bool = False
    run_matching: bool = True

    # 过滤条件
    candidate_status_filter: List[str] = None  # 空表示全部
    job_status_filter: List[str] = None  # 空表示全部

    def __post_init__(self):
        if self.candidate_status_filter is None:
            self.candidate_status_filter = []
        if self.job_status_filter is None:
            self.job_status_filter = []


class DataSyncService:
    """
    数据同步服务

    功能:
    1. 从飞书/Bitable拉取数据
    2. 转换到TalentAI Pro内部格式
    3. 运行智能处理（JD Intelligence, Candidate Intelligence等）
    4. 执行匹配
    5. 更新Deal状态

    使用方式:
    ```python
    config = SyncConfig(
        bitable_app_token="your_app_token",
        bitable_encryption_key="your_key"
    )
    sync_service = DataSyncService(config)

    # 完整同步
    result = sync_service.sync_all()

    # 仅同步候选人
    candidates = sync_service.sync_candidates()

    # 同步并匹配
    matches = sync_service.sync_and_match()
    ```
    """

    def __init__(self, config: SyncConfig = None):
        """
        初始化数据同步服务

        Args:
            config: 同步配置
        """
        self.config = config or SyncConfig()

        # 初始化连接器
        self._init_connectors()

        # 初始化引擎
        self._init_engines()

        # 同步状态缓存
        self._sync_cache: Dict[str, Any] = {}

    def _init_connectors(self):
        """初始化连接器"""
        # 延迟导入避免循环依赖
        try:
            from connectors.feishu import FeishuConnector
            from connectors.bitable import BitableConnector
        except ImportError:
            from .feishu import FeishuConnector
            from .bitable import BitableConnector

        # 飞书连接器
        self.feishu = FeishuConnector(
            app_id=self.config.feishu_app_id,
            app_secret=self.config.feishu_app_secret,
            tenant_access_token=self.config.feishu_tenant_token
        )

        # Bitable连接器
        self.bitable = BitableConnector(
            app_token=self.config.bitable_app_token,
            personal_encryption_key=self.config.bitable_encryption_key
        )

    def _init_engines(self):
        """初始化AI引擎"""
        if JDIntelligenceEngine is not None:
            self.jd_engine = JDIntelligenceEngine()
            self.candidate_engine = CandidateIntelligenceEngine()
            self.discovery_radar = DiscoveryRadar()
            self.matching_engine = MatchingEngineV2()
            self.deal_tracker = DealTracker()
            self.outreach_engine = SmartOutreachEngine()
        else:
            # Mock模式
            self.jd_engine = None
            self.candidate_engine = None
            self.discovery_radar = None
            self.matching_engine = None
            self.deal_tracker = None
            self.outreach_engine = None

    # ==================== 同步方法 ====================

    def sync_candidates(self) -> SyncResult:
        """
        同步候选人数据

        Returns:
            同步结果
        """
        try:
            # 从Bitable获取候选人记录
            records = self.bitable.get_records("tbl_candidates")

            if not records:
                return SyncResult(
                    status=SyncStatus.NO_DATA,
                    data={"source": "bitable", "table": "tbl_candidates"}
                )

            # 过滤状态
            if self.config.candidate_status_filter:
                records = [
                    r for r in records
                    if r.fields.get("状态", "") in self.config.candidate_status_filter
                ]

            # 转换格式
            candidates = []
            for record in records:
                candidate = self.bitable.record_to_candidate(record)
                candidates.append(candidate)

            # 运行Candidate Intelligence
            if self.config.run_candidate_intelligence and self.candidate_engine:
                for candidate in candidates:
                    try:
                        intelligence = self.candidate_engine.analyze_candidate_intelligence(
                            candidate.get("current_title", ""),
                            candidate.get("current_company", ""),
                            candidate.get("skills", []),
                            candidate.get("years_of_experience", 0)
                        )
                        candidate["intelligence"] = intelligence
                    except Exception as e:
                        print(f"Candidate Intelligence error: {e}")

            return SyncResult(
                status=SyncStatus.SUCCESS,
                synced_count=len(candidates),
                data={"candidates": candidates}
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                errors=[str(e)]
            )

    def sync_jobs(self) -> SyncResult:
        """
        同步职位数据

        Returns:
            同步结果
        """
        try:
            # 从Bitable获取职位记录
            records = self.bitable.get_records("tbl_jobs")

            if not records:
                return SyncResult(
                    status=SyncStatus.NO_DATA,
                    data={"source": "bitable", "table": "tbl_jobs"}
                )

            # 过滤状态
            if self.config.job_status_filter:
                records = [
                    r for r in records
                    if r.fields.get("状态", "") in self.config.job_status_filter
                ]

            # 转换格式
            jobs = []
            for record in records:
                job = self.bitable.record_to_job(record)
                jobs.append(job)

            # 运行JD Intelligence
            if self.config.run_jd_intelligence and self.jd_engine:
                for job in jobs:
                    try:
                        intelligence = self.jd_engine.analyze_jd_intelligence(
                            job.get("title", "") + "\n" + job.get("requirements", ""),
                            job.get("responsibilities", "")
                        )
                        job["intelligence"] = intelligence
                    except Exception as e:
                        print(f"JD Intelligence error: {e}")

            return SyncResult(
                status=SyncStatus.SUCCESS,
                synced_count=len(jobs),
                data={"jobs": jobs}
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                errors=[str(e)]
            )

    def sync_deals(self) -> SyncResult:
        """
        同步交易记录

        Returns:
            同步结果
        """
        try:
            # 从Bitable获取交易记录
            records = self.bitable.get_records("tbl_deals")

            # 转换格式
            deals = []
            for record in records:
                deal = self.bitable.record_to_deal(record)
                deals.append(deal)

            return SyncResult(
                status=SyncStatus.SUCCESS,
                synced_count=len(deals),
                data={"deals": deals}
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                errors=[str(e)]
            )

    def sync_calendar_events(self, days: int = 7) -> SyncResult:
        """
        同步日历事件

        Args:
            days: 向前查看的天数

        Returns:
            同步结果
        """
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)

            events = self.feishu.get_calendar_events(start_date, end_date)

            # 转换为Activities
            activities = []
            for event in events:
                activity = self.feishu.calendar_event_to_job(event)
                activities.append(activity)

            return SyncResult(
                status=SyncStatus.SUCCESS,
                synced_count=len(activities),
                data={"activities": activities, "events": events}
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                errors=[str(e)]
            )

    def sync_all(self) -> SyncResult:
        """
        完整同步（候选人 + 职位 + 交易）

        Returns:
            同步结果
        """
        results = {}

        # 同步候选人
        if self.config.sync_candidates:
            results["candidates"] = self.sync_candidates()

        # 同步职位
        if self.config.sync_jobs:
            results["jobs"] = self.sync_jobs()

        # 同步交易
        if self.config.sync_deals:
            results["deals"] = self.sync_deals()

        # 同步日历
        if self.config.sync_calendar:
            results["calendar"] = self.sync_calendar_events()

        # 汇总结果
        total_synced = sum(r.synced_count for r in results.values() if r.status == SyncStatus.SUCCESS)
        total_failed = sum(r.failed_count for r in results.values())

        all_success = all(r.status == SyncStatus.SUCCESS for r in results.values())
        any_failed = any(r.status == SyncStatus.FAILED for r in results.values())

        if all_success:
            status = SyncStatus.SUCCESS
        elif any_failed:
            status = SyncStatus.PARTIAL
        else:
            status = SyncStatus.NO_DATA

        return SyncResult(
            status=status,
            synced_count=total_synced,
            failed_count=total_failed,
            data={k: v.data for k, v in results.items()}
        )

    # ==================== 匹配方法 ====================

    def sync_and_match(self) -> SyncResult:
        """
        同步数据并执行匹配

        Returns:
            同步和匹配结果
        """
        # 完整同步
        sync_result = self.sync_all()

        if sync_result.status == SyncStatus.NO_DATA:
            return sync_result

        candidates = sync_result.data.get("candidates", [])
        jobs = sync_result.data.get("jobs", [])

        if not candidates or not jobs:
            return SyncResult(
                status=SyncStatus.NO_DATA,
                data=sync_result.data
            )

        # 执行匹配
        matches = []
        for candidate in candidates:
            for job in jobs:
                try:
                    # 构建输入
                    candidate_input = {
                        "name": candidate.get("name", ""),
                        "current_title": candidate.get("current_title", ""),
                        "current_company": candidate.get("current_company", ""),
                        "skills": candidate.get("skills", []),
                        "years_of_experience": candidate.get("years_of_experience", 0),
                        "location": candidate.get("location", ""),
                        "expected_salary": candidate.get("expected_salary", 0),
                        "intelligence": candidate.get("intelligence", {})
                    }

                    job_input = {
                        "title": job.get("title", ""),
                        "requirements": job.get("requirements", ""),
                        "responsibilities": job.get("responsibilities", ""),
                        "location": job.get("location", ""),
                        "salary_range": f"{job.get('salary_min', 0)}-{job.get('salary_max', 0)}",
                        "intelligence": job.get("intelligence", {})
                    }

                    # 执行匹配
                    match_result = self.matching_engine.match(candidate_input, job_input)

                    if match_result and match_result.get("overall_score", 0) >= 60:
                        matches.append({
                            "candidate": candidate,
                            "job": job,
                            "match": match_result
                        })

                except Exception as e:
                    print(f"Matching error: {e}")

        # 按匹配分排序
        matches.sort(key=lambda x: x["match"].get("overall_score", 0), reverse=True)

        return SyncResult(
            status=SyncStatus.SUCCESS,
            synced_count=len(matches),
            data={
                **sync_result.data,
                "matches": matches
            }
        )

    # ==================== 创建Deal方法 ====================

    def create_deal_from_match(
        self,
        match: Dict[str, Any],
        stage: DealStage = DealStage.SOURCED
    ) -> Deal:
        """
        从匹配结果创建Deal

        Args:
            match: 匹配结果
            stage: 初始阶段

        Returns:
            创建的Deal
        """
        candidate = match.get("candidate", {})
        job = match.get("job", {})
        match_data = match.get("match", {})

        # 创建Deal
        deal = self.deal_tracker.create_deal(
            candidate_id=candidate.get("source_id", ""),
            candidate_name=candidate.get("name", ""),
            job_id=job.get("source_id", ""),
            job_title=job.get("title", ""),
            company_name=job.get("department", ""),
            stage=stage,
            match_score=match_data.get("overall_score", 0)
        )

        return deal

    def sync_deals_to_bitable(self, deals: List[Deal]) -> SyncResult:
        """
        将Deals同步回Bitable

        Args:
            deals: Deal列表

        Returns:
            同步结果
        """
        try:
            synced = 0
            for deal in deals:
                fields = {
                    "阶段": deal.stage.value,
                    "匹配度": deal.match_score,
                    "面试轮数": deal.interview_rounds,
                    "最后联系": deal.last_contact_date.strftime("%Y-%m-%d") if deal.last_contact_date else None,
                    "下一步行动": deal.next_action,
                    "Offer金额": deal.offer_amount
                }

                # 更新或创建记录
                if deal.source_id:
                    self.bitable.update_record("tbl_deals", deal.source_id, fields)
                else:
                    new_record = self.bitable.create_record("tbl_deals", fields)
                    deal.source_id = new_record.record_id

                synced += 1

            return SyncResult(
                status=SyncStatus.SUCCESS,
                synced_count=synced,
                data={"deals": [d.to_dict() for d in deals]}
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                errors=[str(e)]
            )

    # ==================== 生成推荐邮件 ====================

    def generate_outreach_for_match(self, match: Dict[str, Any]) -> str:
        """
        为匹配结果生成推荐邮件

        Args:
            match: 匹配结果

        Returns:
            邮件内容
        """
        candidate = match.get("candidate", {})
        job = match.get("job", {})
        discovery = match.get("discovery", {})

        # 生成邮件
        email_result = self.outreach_engine.generate_personalized_email(
            candidate_name=candidate.get("name", ""),
            candidate_background=candidate.get("current_title", ""),
            job_title=job.get("title", ""),
            company_name=job.get("department", ""),
            key_surprises=discovery.get("key_findings", [])
        )

        return email_result.get("email_body", "")

    # ==================== 工具方法 ====================

    def get_sync_summary(self) -> Dict[str, Any]:
        """
        获取同步摘要

        Returns:
            摘要信息
        """
        return {
            "feishu_connected": bool(self.config.feishu_app_id),
            "bitable_connected": bool(self.config.bitable_app_token),
            "candidates_table": "tbl_candidates",
            "jobs_table": "tbl_jobs",
            "deals_table": "tbl_deals",
            "last_sync": datetime.now().isoformat(),
            "options": {
                "sync_candidates": self.config.sync_candidates,
                "sync_jobs": self.config.sync_jobs,
                "sync_deals": self.config.sync_deals,
                "run_jd_intelligence": self.config.run_jd_intelligence,
                "run_candidate_intelligence": self.config.run_candidate_intelligence,
                "run_discovery_radar": self.config.run_discovery_radar,
                "run_matching": self.config.run_matching
            }
        }


# ==================== 便捷函数 ====================

def create_sync_service(
    bitable_app_token: str = None,
    bitable_encryption_key: str = None,
    feishu_app_id: str = None,
    feishu_app_secret: str = None,
    **kwargs
) -> DataSyncService:
    """
    创建数据同步服务的便捷函数

    Args:
        bitable_app_token: Bitable应用Token
        bitable_encryption_key: Bitable加密密钥
        feishu_app_id: 飞书App ID
        feishu_app_secret: 飞书App Secret
        **kwargs: 其他SyncConfig选项

    Returns:
        DataSyncService实例
    """
    config = SyncConfig(
        bitable_app_token=bitable_app_token or "",
        bitable_encryption_key=bitable_encryption_key or "",
        feishu_app_id=feishu_app_id or "",
        feishu_app_secret=feishu_app_secret or "",
        **kwargs
    )
    return DataSyncService(config)


if __name__ == "__main__":
    # 快速测试
    sync_service = create_sync_service()

    print("=== 测试数据同步服务 ===")

    # 获取同步摘要
    summary = sync_service.get_sync_summary()
    print(f"配置: {json.dumps(summary, ensure_ascii=False, indent=2)}")

    # 同步候选人
    print("\n--- 同步候选人 ---")
    result = sync_service.sync_candidates()
    print(f"状态: {result.status.value}")
    print(f"数量: {result.synced_count}")
    if result.data.get("candidates"):
        c = result.data["candidates"][0]
        print(f"示例: {c.get('name')} - {c.get('current_title')}")

    # 同步职位
    print("\n--- 同步职位 ---")
    result = sync_service.sync_jobs()
    print(f"状态: {result.status.value}")
    print(f"数量: {result.synced_count}")
    if result.data.get("jobs"):
        j = result.data["jobs"][0]
        print(f"示例: {j.get('title')} - {j.get('department')}")

    # 同步并匹配
    print("\n--- 同步并匹配 ---")
    result = sync_service.sync_and_match()
    print(f"状态: {result.status.value}")
    print(f"匹配数: {result.synced_count}")
    if result.data.get("matches"):
        m = result.data["matches"][0]
        print(f"最佳匹配: {m['candidate'].get('name')} -> {m['job'].get('title')}")
        print(f"匹配分: {m['match'].get('overall_score')}")
