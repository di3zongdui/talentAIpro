# -*- coding: utf-8 -*-
"""
Bitable (飞书多维表格) 连接器 - TalentAI Pro
支持: 数据表读取、记录同步、字段映射
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class BitableFieldType(Enum):
    """Bitable字段类型"""
    TEXT = "text"
    NUMBER = "number"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    USER = "user"
    FILE = "file"
    LINK = "link"
    LOOKUP = "lookup"
    FORMULA = "formula"
    UNKNOWN = "unknown"


@dataclass
class BitableField:
    """Bitable字段定义"""
    field_id: str
    name: str
    type: BitableFieldType = BitableFieldType.TEXT
    description: str = ""


@dataclass
class BitableRecord:
    """Bitable记录"""
    record_id: str
    fields: Dict[str, Any] = field(default_factory=dict)
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


@dataclass
class BitableTable:
    """Bitable数据表"""
    table_id: str
    name: str
    fields: List[BitableField] = field(default_factory=list)
    records: List[BitableRecord] = field(default_factory=list)


@dataclass
class BitableApp:
    """Bitable多维表格应用"""
    app_token: str
    name: str
    tables: List[BitableTable] = field(default_factory=list)


class BitableConnector:
    """
    Bitable (飞书多维表格) 连接器

    功能:
    1. 获取数据表列表
    2. 获取数据表字段定义
    3. 获取数据记录
    4. 创建/更新记录
    5. 字段映射到TalentAI Pro模型

    使用方式:
    ```python
    connector = BitableConnector(app_token="your_app_token", personal_encryption_key="your_key")

    # 获取所有表
    app = connector.get_app()

    # 获取记录
    records = connector.get_records("table_id")

    # 同步到TalentAI Pro
    jobs = connector.records_to_jobs(records)
    ```

    Bitable数据表结构示例 (CGL招聘跟踪表):
    | 候选人 | 职位 | 状态 | 面试时间 | 推荐度 | 备注 |
    |--------|------|------|----------|--------|------|
    | 张三   | AI产品经理 | 面试中 | 2026-04-25 | 85 | 二次面试 |
    """

    def __init__(
        self,
        app_token: str = "",
        personal_encryption_key: str = ""
    ):
        """
        初始化Bitable连接器

        Args:
            app_token: Bitable应用Token
            personal_encryption_key: 个人加密密钥
        """
        self.app_token = app_token
        self.personal_encryption_key = personal_encryption_key
        self.base_url = "https://open.feishu.cn/open-apis/bitable/v1"

        # 缓存
        self._app_cache: Optional[BitableApp] = None
        self._cache_time = 0
        self._cache_ttl = 300  # 5分钟缓存

    def _make_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "Authorization": f"Bearer {self.personal_encryption_key}",
            "Content-Type": "application/json"
        }

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (
            self._app_cache is not None and
            time.time() - self._cache_time < self._cache_ttl
        )

    # ==================== App级别API ====================

    def get_app(self, force_refresh: bool = False) -> Optional[BitableApp]:
        """
        获取Bitable应用信息

        Args:
            force_refresh: 强制刷新缓存

        Returns:
            BitableApp对象
        """
        if self._is_cache_valid() and not force_refresh:
            return self._app_cache

        if not self.app_token:
            return self._mock_app()

        # TODO: 实际API调用
        # GET /apps/{app_token}

        app = self._mock_app()
        self._app_cache = app
        self._cache_time = time.time()
        return app

    def _mock_app(self) -> BitableApp:
        """生成Mock Bitable App"""
        return BitableApp(
            app_token=self.app_token or "mock_app_token",
            name="CGL招聘跟踪表",
            tables=[
                BitableTable(
                    table_id="tbl_candidates",
                    name="候选人库",
                    fields=[
                        BitableField("fld_name", "姓名", BitableFieldType.TEXT),
                        BitableField("fld_email", "邮箱", BitableFieldType.TEXT),
                        BitableField("fld_phone", "电话", BitableFieldType.TEXT),
                        BitableField("fld_title", "当前职位", BitableFieldType.TEXT),
                        BitableField("fld_company", "当前公司", BitableFieldType.TEXT),
                        BitableField("fld_experience", "工作年限", BitableFieldType.NUMBER),
                        BitableField("fld_skills", "核心技能", BitableFieldType.MULTI_SELECT),
                        BitableField("fld_location", "所在地", BitableFieldType.TEXT),
                        BitableField("fld_salary", "期望薪资", BitableFieldType.NUMBER),
                        BitableField("fld_status", "状态", BitableFieldType.SINGLE_SELECT),
                        BitableField("fld_source", "来源", BitableFieldType.SINGLE_SELECT),
                        BitableField("fld_remark", "备注", BitableFieldType.TEXT),
                        BitableField("fld_interview_date", "面试日期", BitableFieldType.DATE),
                        BitableField("fld_match_score", "匹配度", BitableFieldType.NUMBER),
                    ],
                    records=self._mock_candidate_records()
                ),
                BitableTable(
                    table_id="tbl_jobs",
                    name="职位库",
                    fields=[
                        BitableField("fld_title", "职位名称", BitableFieldType.TEXT),
                        BitableField("fld_department", "部门", BitableFieldType.TEXT),
                        BitableField("fld_location", "工作地点", BitableFieldType.TEXT),
                        BitableField("fld_salary_min", "薪资下限", BitableFieldType.NUMBER),
                        BitableField("fld_salary_max", "薪资上限", BitableFieldType.NUMBER),
                        BitableField("fld_requirements", "任职要求", BitableFieldType.TEXT),
                        BitableField("fld_responsibilities", "岗位职责", BitableFieldType.TEXT),
                        BitableField("fld_priority", "优先级", BitableFieldType.SINGLE_SELECT),
                        BitableField("fld_status", "状态", BitableFieldType.SINGLE_SELECT),
                        BitableField("fld_hiring_manager", "招聘经理", BitableFieldType.USER),
                        BitableField("fld_open_date", "开放日期", BitableFieldType.DATE),
                        BitableField("fld_close_date", "关闭日期", BitableFieldType.DATE),
                    ],
                    records=self._mock_job_records()
                ),
                BitableTable(
                    table_id="tbl_deals",
                    name="招聘交易跟踪",
                    fields=[
                        BitableField("fld_candidate_id", "候选人", BitableFieldType.LINK),
                        BitableField("fld_job_id", "职位", BitableFieldType.LINK),
                        BitableField("fld_stage", "阶段", BitableFieldType.SINGLE_SELECT),
                        BitableField("fld_match_score", "匹配度", BitableFieldType.NUMBER),
                        BitableField("fld_interview_rounds", "面试轮数", BitableFieldType.NUMBER),
                        BitableField("fld_last_contact", "最后联系", BitableFieldType.DATE),
                        BitableField("fld_next_action", "下一步行动", BitableFieldType.TEXT),
                        BitableField("fld_offer_amount", "Offer金额", BitableFieldType.NUMBER),
                        BitableField("fld_close_reason", "关闭原因", BitableFieldType.SINGLE_SELECT),
                    ],
                    records=[]
                )
            ]
        )

    def _mock_candidate_records(self) -> List[BitableRecord]:
        """生成Mock候选人记录"""
        return [
            BitableRecord(
                record_id="rec_001",
                fields={
                    "姓名": "李明",
                    "邮箱": "liming@email.com",
                    "电话": "13800138000",
                    "当前职位": "高级AI产品经理",
                    "当前公司": "某知名AI公司",
                    "工作年限": 8,
                    "核心技能": ["AI产品", "数据分析", "团队管理"],
                    "所在地": "北京",
                    "期望薪资": 800000,
                    "状态": "面试中",
                    "来源": "LinkedIn",
                    "备注": "3年AI经验，表达能力好",
                    "面试日期": "2026-04-25",
                    "匹配度": 85
                },
                created_time=datetime.now() - timedelta(days=10),
                updated_time=datetime.now() - timedelta(days=1)
            ),
            BitableRecord(
                record_id="rec_002",
                fields={
                    "姓名": "王芳",
                    "邮箱": "wangfang@email.com",
                    "电话": "13900139000",
                    "当前职位": "AI技术总监",
                    "当前公司": "某创业公司",
                    "工作年限": 12,
                    "核心技能": ["AI技术", "算法", "研发管理"],
                    "所在地": "上海",
                    "期望薪资": 1500000,
                    "状态": "Offer",
                    "来源": "猎头",
                    "备注": "技术背景强，成功率高",
                    "面试日期": "2026-04-20",
                    "匹配度": 92
                },
                created_time=datetime.now() - timedelta(days=20),
                updated_time=datetime.now() - timedelta(days=2)
            ),
            BitableRecord(
                record_id="rec_003",
                fields={
                    "姓名": "张伟",
                    "邮箱": "zhangwei@email.com",
                    "电话": "13700137000",
                    "当前职位": "产品副总裁",
                    "当前公司": "某上市公司",
                    "工作年限": 15,
                    "核心技能": ["产品战略", "团队建设", "商业化"],
                    "所在地": "深圳",
                    "期望薪资": 2000000,
                    "状态": "筛选中",
                    "来源": "内部推荐",
                    "备注": "资历深，需进一步沟通",
                    "匹配度": 78
                },
                created_time=datetime.now() - timedelta(days=5),
                updated_time=datetime.now() - timedelta(days=5)
            )
        ]

    def _mock_job_records(self) -> List[BitableRecord]:
        """生成Mock职位记录"""
        return [
            BitableRecord(
                record_id="job_001",
                fields={
                    "职位名称": "AI产品总监",
                    "部门": "AI产品部",
                    "工作地点": "北京",
                    "薪资下限": 800000,
                    "薪资上限": 1500000,
                    "任职要求": "5年以上AI产品经验，有团队管理经验",
                    "岗位职责": "负责AI产品规划与团队管理",
                    "优先级": "高",
                    "状态": "开放",
                    "招聘经理": "HR张总",
                    "开放日期": "2026-04-01"
                },
                created_time=datetime.now() - timedelta(days=20),
                updated_time=datetime.now() - timedelta(days=3)
            ),
            BitableRecord(
                record_id="job_002",
                fields={
                    "职位名称": "高级AI算法工程师",
                    "部门": "AI研发部",
                    "工作地点": "上海",
                    "薪资下限": 600000,
                    "薪资上限": 1200000,
                    "任职要求": "3年以上算法经验，熟悉深度学习",
                    "岗位职责": "负责AI算法研发与优化",
                    "优先级": "高",
                    "状态": "开放",
                    "招聘经理": "技术李总",
                    "开放日期": "2026-04-10"
                },
                created_time=datetime.now() - timedelta(days=10),
                updated_time=datetime.now() - timedelta(days=1)
            )
        ]

    # ==================== Table级别API ====================

    def get_tables(self) -> List[BitableTable]:
        """
        获取所有数据表

        Returns:
            数据表列表
        """
        app = self.get_app()
        return app.tables if app else []

    def get_table(self, table_id: str) -> Optional[BitableTable]:
        """
        获取指定数据表

        Args:
            table_id: 数据表ID

        Returns:
            数据表对象
        """
        tables = self.get_tables()
        for table in tables:
            if table.table_id == table_id:
                return table
        return None

    def get_fields(self, table_id: str) -> List[BitableField]:
        """
        获取数据表字段定义

        Args:
            table_id: 数据表ID

        Returns:
            字段列表
        """
        table = self.get_table(table_id)
        return table.fields if table else []

    # ==================== Record级别API ====================

    def get_records(
        self,
        table_id: str,
        filter_formula: str = "",
        limit: int = 100,
        offset: str = ""
    ) -> List[BitableRecord]:
        """
        获取数据记录

        Args:
            table_id: 数据表ID
            filter_formula: 过滤公式
            limit: 返回记录数限制
            offset: 分页偏移

        Returns:
            记录列表
        """
        table = self.get_table(table_id)
        if not table:
            return []

        records = table.records[:limit]
        return records

    def get_record(self, table_id: str, record_id: str) -> Optional[BitableRecord]:
        """
        获取单条记录

        Args:
            table_id: 数据表ID
            record_id: 记录ID

        Returns:
            记录对象
        """
        records = self.get_records(table_id)
        for record in records:
            if record.record_id == record_id:
                return record
        return None

    def create_record(
        self,
        table_id: str,
        fields: Dict[str, Any]
    ) -> BitableRecord:
        """
        创建记录

        Args:
            table_id: 数据表ID
            fields: 字段数据

        Returns:
            创建的记录
        """
        if not self.app_token:
            record = BitableRecord(
                record_id=f"rec_{int(time.time())}",
                fields=fields,
                created_time=datetime.now(),
                updated_time=datetime.now()
            )
            return record

        # TODO: 实际API调用
        # POST /apps/{app_token}/tables/{table_id}/records

        return BitableRecord(
            record_id=f"rec_{int(time.time())}",
            fields=fields,
            created_time=datetime.now(),
            updated_time=datetime.now()
        )

    def update_record(
        self,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> bool:
        """
        更新记录

        Args:
            table_id: 数据表ID
            record_id: 记录ID
            fields: 要更新的字段

        Returns:
            是否更新成功
        """
        if not self.app_token:
            return True

        # TODO: 实际API调用
        # PUT /apps/{app_token}/tables/{table_id}/records/{record_id}

        return True

    # ==================== 数据转换 ====================

    def record_to_candidate(self, record: BitableRecord) -> Dict[str, Any]:
        """
        将Bitable记录转换为Candidate格式

        Args:
            record: Bitable记录

        Returns:
            Candidate格式的字典
        """
        fields = record.fields

        return {
            "name": fields.get("姓名", ""),
            "email": fields.get("邮箱", ""),
            "phone": fields.get("电话", ""),
            "current_title": fields.get("当前职位", ""),
            "current_company": fields.get("当前公司", ""),
            "years_of_experience": fields.get("工作年限", 0),
            "skills": fields.get("核心技能", []),
            "location": fields.get("所在地", ""),
            "expected_salary": fields.get("期望薪资", 0),
            "status": fields.get("状态", ""),
            "source": fields.get("来源", ""),
            "remarks": fields.get("备注", ""),
            "interview_date": fields.get("面试日期", ""),
            "match_score": fields.get("匹配度", 0),
            "source": "bitable",
            "source_id": record.record_id,
            "created_at": record.created_time.isoformat() if record.created_time else None,
            "updated_at": record.updated_time.isoformat() if record.updated_time else None
        }

    def record_to_job(self, record: BitableRecord) -> Dict[str, Any]:
        """
        将Bitable记录转换为Job格式

        Args:
            record: Bitable记录

        Returns:
            Job格式的字典
        """
        fields = record.fields

        return {
            "title": fields.get("职位名称", ""),
            "department": fields.get("部门", ""),
            "location": fields.get("工作地点", ""),
            "salary_min": fields.get("薪资下限", 0),
            "salary_max": fields.get("薪资上限", 0),
            "requirements": fields.get("任职要求", ""),
            "responsibilities": fields.get("岗位职责", ""),
            "priority": fields.get("优先级", ""),
            "status": fields.get("状态", ""),
            "hiring_manager": fields.get("招聘经理", ""),
            "open_date": fields.get("开放日期", ""),
            "close_date": fields.get("关闭日期", ""),
            "source": "bitable",
            "source_id": record.record_id,
            "created_at": record.created_time.isoformat() if record.created_time else None,
            "updated_at": record.updated_time.isoformat() if record.updated_time else None
        }

    def record_to_deal(self, record: BitableRecord) -> Dict[str, Any]:
        """
        将Bitable记录转换为Deal格式

        Args:
            record: Bitable记录

        Returns:
            Deal格式的字典
        """
        fields = record.fields

        return {
            "candidate_id": fields.get("候选人", ""),
            "job_id": fields.get("职位", ""),
            "stage": fields.get("阶段", ""),
            "match_score": fields.get("匹配度", 0),
            "interview_rounds": fields.get("面试轮数", 0),
            "last_contact": fields.get("最后联系", ""),
            "next_action": fields.get("下一步行动", ""),
            "offer_amount": fields.get("Offer金额", 0),
            "close_reason": fields.get("关闭原因", ""),
            "source": "bitable",
            "source_id": record.record_id,
            "created_at": record.created_time.isoformat() if record.created_time else None,
            "updated_at": record.updated_time.isoformat() if record.updated_time else None
        }

    def records_to_candidates(self, records: List[BitableRecord]) -> List[Dict[str, Any]]:
        """批量转换记录为候选人格式"""
        return [self.record_to_candidate(r) for r in records]

    def records_to_jobs(self, records: List[BitableRecord]) -> List[Dict[str, Any]]:
        """批量转换记录为职位格式"""
        return [self.record_to_job(r) for r in records]


# ==================== 便捷函数 ====================

def create_bitable_connector(
    app_token: str = None,
    personal_encryption_key: str = None
) -> BitableConnector:
    """
    创建Bitable连接器的便捷函数

    Args:
        app_token: Bitable应用Token
        personal_encryption_key: 个人加密密钥

    Returns:
        BitableConnector实例
    """
    return BitableConnector(
        app_token=app_token or "",
        personal_encryption_key=personal_encryption_key or ""
    )


if __name__ == "__main__":
    # 快速测试
    connector = create_bitable_connector()

    print("=== 测试Bitable连接器 ===")

    # 获取App
    app = connector.get_app()
    print(f"App: {app.name}")
    print(f"数据表: {[t.name for t in app.tables]}")

    # 获取候选人
    candidates_table = connector.get_table("tbl_candidates")
    if candidates_table:
        records = connector.get_records("tbl_candidates")
        print(f"\n候选人记录: {len(records)}")
        for rec in records:
            fields = rec.fields
            print(f"  - {fields.get('姓名')} | {fields.get('当前职位')} | {fields.get('状态')}")

        # 测试转换
        if records:
            candidate = connector.record_to_candidate(records[0])
            print(f"\n转换后: {candidate['name']} - {candidate['match_score']}")
