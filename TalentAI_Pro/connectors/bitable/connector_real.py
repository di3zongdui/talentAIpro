# -*- coding: utf-8 -*-
"""
飞书Bitable（多维表格）真实API连接器 - TalentAI Pro
用于候选人库、职位库、交易跟踪数据同步

Bitable API文档: https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/

创建应用流程:
1. 访问 https://open.feishu.cn/app 登录
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 配置权限:
   - bitable:app:readonly 多维表格只读
   - bitable:app:write 多维表格读写
5. 将应用添加到你需要操作的多维表格中
6. 在多维表格中获取 App Token 和 Table ID

配置示例:
    cp config_bitables.py.example config_bitables.py
    # 编辑 config_bitables.py 填入真实值
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum


# ============================================================
# 配置文件示例
# ============================================================

BITABLE_CONFIG_EXAMPLE = """
# Bitable连接器配置 - 复制此文件为 config_bitables.py 并填入真实值

# 飞书应用凭证（用于获取tenant_access_token）
BITABLE_APP_ID = "cli_xxxxxxxxxxxxxxxxxx"
BITABLE_APP_SECRET = "your_app_secret_here"

# 多维表格 App Token（从多维表格URL获取）
# URL格式: https://xxx.feishu.cn/base/xxxxxx
# App Token: xxxxxx（9位字母）
BITABLE_APP_TOKEN = "MKLxxxxxxxx"

# 数据表配置
# Table ID 从多维表格中获取
TABLES = {
    "candidates": "tblxxxxxxxx",      # 候选人库
    "jobs": "tblxxxxxxxx",            # 职位库
    "deals": "tblxxxxxxxx",           # 招聘交易跟踪
    "activities": "tblxxxxxxxx"       # 活动记录
}

# 字段映射配置
FIELD_MAPPING = {
    "candidates": {
        "name": "姓名",
        "email": "邮箱",
        "phone": "手机",
        "title": "当前职位",
        "company": "当前公司",
        "skills": "技能",
        "experience_years": "工作年限",
        "current_salary": "当前薪资",
        "expected_salary": "期望薪资",
        "status": "状态"
    },
    "jobs": {
        "title": "职位名称",
        "company": "公司",
        "skills_required": "所需技能",
        "experience_years_min": "最低工作年限",
        "salary_min": "薪资下限",
        "salary_max": "薪资上限",
        "location": "地点",
        "status": "状态"
    },
    "deals": {
        "candidate_id": "候选人ID",
        "job_id": "职位ID",
        "stage": "阶段",
        "probability": "意向概率",
        "interview_date": "面试日期",
        "feedback": "反馈",
        "owner": "负责顾问"
    }
}
"""


# ============================================================
# 枚举定义
# ============================================================

class DealStage(Enum):
    """交易阶段"""
    NEW = "new"                        # 新建
    INITIAL_CONTACT = "initial_contact"  # 初步联系
    INTERVIEW_SCHEDULED = "interview_scheduled"  # 面试已安排
    INTERVIEW_COMPLETED = "interview_completed"  # 面试完成
    OFFER_EXTENDED = "offer_extended"  # Offer已发出
    OFFER_ACCEPTED = "offer_accepted"  # Offer已接受
    HIRED = "hired"                    # 已入职
    REJECTED = "rejected"              # 拒绝
    WITHDRAWN = "withdrawn"            # 撤回


class CandidateStatus(Enum):
    """候选人状态"""
    ACTIVE = "active"                  # 活跃
    PASSIVE = "passive"                # 被动
    INTERVIEWING = "interviewing"      # 面试中
    OFFERED = "offered"                # 已Offer
    HIRED = "hired"                    # 已入职
    REJECTED = "rejected"              # 已拒绝


class JobStatus(Enum):
    """职位状态"""
    OPEN = "open"                      # 开放
    FILLED = "filled"                  # 已填充
    CLOSED = "closed"                  # 关闭
    ON_HOLD = "on_hold"                # 暂停


# ============================================================
# 数据类定义
# ============================================================

@dataclass
class BitableRecord:
    """Bitable记录基础类"""
    record_id: str = ""


@dataclass
class Candidate(BitableRecord):
    """候选人"""
    name: str = ""
    email: str = ""
    phone: str = ""
    title: str = ""
    company: str = ""
    skills: List[str] = field(default_factory=list)
    experience_years: int = 0
    current_salary: str = ""
    expected_salary: str = ""
    status: CandidateStatus = CandidateStatus.ACTIVE
    source: str = ""
    notes: str = ""


@dataclass
class Job(BitableRecord):
    """职位"""
    title: str = ""
    company: str = ""
    skills_required: List[str] = field(default_factory=list)
    experience_years_min: int = 0
    salary_min: str = ""
    salary_max: str = ""
    location: str = ""
    status: JobStatus = JobStatus.OPEN
    priority: str = ""
    notes: str = ""


@dataclass
class Deal(BitableRecord):
    """招聘交易"""
    candidate_id: str = ""
    job_id: str = ""
    candidate_name: str = ""
    job_title: str = ""
    stage: DealStage = DealStage.NEW
    probability: int = 0
    interview_date: Optional[datetime] = None
    feedback: str = ""
    owner: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Activity(BitableRecord):
    """活动记录"""
    deal_id: str = ""
    activity_type: str = ""
    content: str = ""
    timestamp: Optional[datetime] = None


# ============================================================
# Bitable连接器
# ============================================================

class BitableConnectorReal:
    """
    飞书Bitable（多维表格）连接器 - 真实API版本

    支持功能:
    1. 候选人库管理 - CRUD操作
    2. 职位库管理 - CRUD操作
    3. 交易跟踪 - 状态更新
    4. 活动记录 - 日志追踪

    使用示例:
    ```python
    # 方式1: 使用配置文件
    from config_bitables import BITABLE_APP_ID, BITABLE_APP_SECRET, BITABLE_APP_TOKEN, TABLES
    connector = BitableConnectorReal(
        app_id=BITABLE_APP_ID,
        app_secret=BITABLE_APP_SECRET,
        app_token=BITABLE_APP_TOKEN
    )

    # 方式2: 直接传入
    connector = BitableConnectorReal(
        app_id="cli_xxx",
        app_secret="secret_xxx",
        app_token="MKLxxx",
        tables={
            "candidates": "tblxxx",
            "jobs": "tblxxx",
            "deals": "tblxxx"
        }
    )

    # 获取所有候选人
    candidates = connector.get_all_records("candidates")

    # 创建候选人
    new_candidate = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "title": "AI算法工程师"
    }
    record = connector.create_record("candidates", new_candidate)

    # 更新交易阶段
    connector.update_deal_stage("deals", "record_id", DealStage.INTERVIEW_SCHEDULED)
    ```
    """

    def __init__(
        self,
        app_id: str = "",
        app_secret: str = "",
        app_token: str = "",
        tables: Dict[str, str] = None,
        field_mapping: Dict[str, Dict[str, str]] = None
    ):
        """
        初始化Bitable连接器

        Args:
            app_id: 飞书应用 App ID
            app_secret: 飞书应用 App Secret
            app_token: 多维表格 App Token
            tables: 数据表映射 {"candidates": "tblxxx", ...}
            field_mapping: 字段映射配置
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.tables = tables or {}
        self.field_mapping = field_mapping or {}

        self.base_url = "https://open.feishu.cn/open-apis"

        # Token缓存
        self._token_cache = {
            "token": "",
            "expires_at": 0
        }

        # API端点
        self._endpoints = {
            "auth": "/auth/v3/tenant_access_token/internal",
            "records": "/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            "record_detail": "/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            "fields": "/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            "batch_create": "/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            "batch_update": "/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        }

        # 验证配置
        self._validate_config()

    def _validate_config(self) -> None:
        """验证连接器配置"""
        if not self.app_id and not self.app_secret:
            print("[WARNING] BitableConnector running in MOCK mode - no credentials provided")
            print("  To enable real API calls:")
            print("    1. Create app at https://open.feishu.cn/app")
            print("    2. Get App Token from your Bitable URL")
            print("    3. Get Table IDs from your Bitable")
            print("    4. Create config_bitables.py with credentials")

    def _get_access_token(self) -> str:
        """获取访问令牌"""
        # 检查缓存
        if self._token_cache["token"] and time.time() < self._token_cache["expires_at"] - 60:
            return self._token_cache["token"]

        if not self.app_id or not self.app_secret:
            return "mock_token"

        url = f"{self.base_url}{self._endpoints['auth']}"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"Failed to get access token: {result.get('msg')}")

        self._token_cache = {
            "token": result.get("tenant_access_token", ""),
            "expires_at": time.time() + 7200
        }

        return self._token_cache["token"]

    def _make_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

    def _api_call(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None,
        retries: int = 3
    ) -> Dict:
        """通用API调用"""
        url = f"{self.base_url}{endpoint}"
        headers = self._make_headers()

        for attempt in range(retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=headers, json=json_data, timeout=10)
                elif method.upper() == "PUT":
                    response = requests.put(url, headers=headers, json=json_data, timeout=10)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, params=params, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                result = response.json()

                if result.get("code") == 0:
                    return result.get("data", {})

                if result.get("code") == 99991663 and attempt < retries - 1:
                    self._token_cache = {"token": "", "expires_at": 0}
                    time.sleep(1)
                    headers = self._make_headers()
                    continue

                raise Exception(f"API error: code={result.get('code')}, msg={result.get('msg')}")

            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                raise Exception(f"Request failed: {str(e)}")

        raise Exception("Max retries exceeded")

    # ==================== 记录操作 ====================

    def get_all_records(
        self,
        table_name: str,
        filter_formula: str = None,
        sort_config: List[Dict] = None,
        page_size: int = 100
    ) -> List[Dict]:
        """
        获取表的所有记录

        Args:
            table_name: 表名 (candidates/jobs/deals)
            filter_formula: 过滤公式
            sort_config: 排序配置
            page_size: 每页大小

        Returns:
            记录列表
        """
        if table_name not in self.tables:
            print(f"[WARNING] Table '{table_name}' not configured, returning mock data")
            return self._mock_get_records(table_name)

        table_id = self.tables[table_name]
        endpoint = self._endpoints["records"].format(
            app_token=self.app_token,
            table_id=table_id
        )

        all_records = []
        page_token = None

        while True:
            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            if filter_formula:
                params["filter_formula"] = filter_formula
            if sort_config:
                params["sort"] = json.dumps(sort_config)

            data = self._api_call("GET", endpoint, params=params)
            items = data.get("items", [])
            all_records.extend(items)

            if not data.get("has_more"):
                break

            page_token = data.get("next_page_token")

        return all_records

    def get_record(self, table_name: str, record_id: str) -> Optional[Dict]:
        """
        获取单条记录

        Args:
            table_name: 表名
            record_id: 记录ID

        Returns:
            记录数据
        """
        if table_name not in self.tables:
            return self._mock_get_record(table_name, record_id)

        table_id = self.tables[table_name]
        endpoint = self._endpoints["record_detail"].format(
            app_token=self.app_token,
            table_id=table_id,
            record_id=record_id
        )

        data = self._api_call("GET", endpoint)
        return data.get("record", {})

    def create_record(self, table_name: str, fields: Dict) -> Dict:
        """
        创建记录

        Args:
            table_name: 表名
            fields: 字段数据 {"字段名": 值}

        Returns:
            创建的记录
        """
        if table_name not in self.tables:
            print(f"[WARNING] Table '{table_name}' not configured, using mock mode")
            return self._mock_create_record(table_name, fields)

        table_id = self.tables[table_name]
        endpoint = self._endpoints["records"].format(
            app_token=self.app_token,
            table_id=table_id
        )

        payload = {"fields": fields}
        data = self._api_call("POST", endpoint, json_data=payload)

        return data.get("record", {})

    def update_record(self, table_name: str, record_id: str, fields: Dict) -> Dict:
        """
        更新记录

        Args:
            table_name: 表名
            record_id: 记录ID
            fields: 更新的字段数据

        Returns:
            更新后的记录
        """
        if table_name not in self.tables:
            return self._mock_update_record(table_name, record_id, fields)

        table_id = self.tables[table_name]
        endpoint = self._endpoints["record_detail"].format(
            app_token=self.app_token,
            table_id=table_id,
            record_id=record_id
        )

        payload = {"fields": fields}
        data = self._api_call("PUT", endpoint, json_data=payload)

        return data.get("record", {})

    def delete_record(self, table_name: str, record_id: str) -> bool:
        """
        删除记录

        Args:
            table_name: 表名
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        if table_name not in self.tables:
            print(f"[WARNING] Mock mode - record not deleted")
            return True

        table_id = self.tables[table_name]
        endpoint = self._endpoints["record_detail"].format(
            app_token=self.app_token,
            table_id=table_id,
            record_id=record_id
        )

        self._api_call("DELETE", endpoint)
        return True

    def batch_create_records(self, table_name: str, records: List[Dict]) -> List[Dict]:
        """
        批量创建记录

        Args:
            table_name: 表名
            records: 记录列表

        Returns:
            创建的记录列表
        """
        if table_name not in self.tables:
            return [self._mock_create_record(table_name, r) for r in records]

        table_id = self.tables[table_name]
        endpoint = self._endpoints["batch_create"].format(
            app_token=self.app_token,
            table_id=table_id
        )

        payload = {
            "records": [{"fields": r} for r in records]
        }

        data = self._api_call("POST", endpoint, json_data=payload)
        return data.get("records", [])

    # ==================== 便捷方法 ====================

    def get_candidates(self, status: str = None) -> List[Candidate]:
        """获取候选人列表"""
        records = self.get_all_records("candidates")

        candidates = []
        for item in records:
            fields = item.get("fields", {})
            candidates.append(Candidate(
                record_id=item.get("record_id", ""),
                name=fields.get("姓名", ""),
                email=fields.get("邮箱", ""),
                phone=fields.get("手机", ""),
                title=fields.get("当前职位", ""),
                company=fields.get("当前公司", ""),
                skills=fields.get("技能", []),
                experience_years=fields.get("工作年限", 0),
                status=CandidateStatus(fields.get("状态", "active")),
                source=fields.get("来源", ""),
                notes=fields.get("备注", "")
            ))

        if status:
            candidates = [c for c in candidates if c.status.value == status]

        return candidates

    def get_jobs(self, status: str = None) -> List[Job]:
        """获取职位列表"""
        records = self.get_all_records("jobs")

        jobs = []
        for item in records:
            fields = item.get("fields", {})
            jobs.append(Job(
                record_id=item.get("record_id", ""),
                title=fields.get("职位名称", ""),
                company=fields.get("公司", ""),
                skills_required=fields.get("所需技能", []),
                experience_years_min=fields.get("最低工作年限", 0),
                salary_min=fields.get("薪资下限", ""),
                salary_max=fields.get("薪资上限", ""),
                location=fields.get("地点", ""),
                status=JobStatus(fields.get("状态", "open")),
                priority=fields.get("优先级", ""),
                notes=fields.get("备注", "")
            ))

        if status:
            jobs = [j for j in jobs if j.status.value == status]

        return jobs

    def get_deals(
        self,
        stage: str = None,
        owner: str = None
    ) -> List[Deal]:
        """获取交易列表"""
        records = self.get_all_records("deals")

        deals = []
        for item in records:
            fields = item.get("fields", {})

            interview_date = fields.get("面试日期")
            if isinstance(interview_date, str):
                try:
                    interview_date = datetime.fromisoformat(interview_date.replace("Z", "+00:00"))
                except:
                    interview_date = None

            deals.append(Deal(
                record_id=item.get("record_id", ""),
                candidate_id=fields.get("候选人ID", ""),
                job_id=fields.get("职位ID", ""),
                candidate_name=fields.get("候选人姓名", ""),
                job_title=fields.get("职位名称", ""),
                stage=DealStage(fields.get("阶段", "new")),
                probability=fields.get("意向概率", 0),
                interview_date=interview_date,
                feedback=fields.get("反馈", ""),
                owner=fields.get("负责顾问", ""),
                created_at=item.get("created_time"),
                updated_at=item.get("last_modified_time"])
            )

        if stage:
            deals = [d for d in deals if d.stage.value == stage]
        if owner:
            deals = [d for d in deals if d.owner == owner]

        return deals

    def update_deal_stage(
        self,
        record_id: str,
        new_stage: DealStage,
        feedback: str = None
    ) -> bool:
        """
        更新交易阶段

        Args:
            record_id: 交易记录ID
            new_stage: 新阶段
            feedback: 反馈

        Returns:
            是否更新成功
        """
        fields = {"阶段": new_stage.value}
        if feedback:
            fields["反馈"] = feedback

        self.update_record("deals", record_id, fields)
        return True

    def create_candidate(self, candidate: Candidate) -> Candidate:
        """创建候选人"""
        record = self.create_record("candidates", {
            "姓名": candidate.name,
            "邮箱": candidate.email,
            "手机": candidate.phone,
            "当前职位": candidate.title,
            "当前公司": candidate.company,
            "技能": candidate.skills,
            "工作年限": candidate.experience_years,
            "当前薪资": candidate.current_salary,
            "期望薪资": candidate.expected_salary,
            "状态": candidate.status.value,
            "来源": candidate.source,
            "备注": candidate.notes
        })

        candidate.record_id = record.get("record_id", "")
        return candidate

    def create_job(self, job: Job) -> Job:
        """创建职位"""
        record = self.create_record("jobs", {
            "职位名称": job.title,
            "公司": job.company,
            "所需技能": job.skills_required,
            "最低工作年限": job.experience_years_min,
            "薪资下限": job.salary_min,
            "薪资上限": job.salary_max,
            "地点": job.location,
            "状态": job.status.value,
            "优先级": job.priority,
            "备注": job.notes
        })

        job.record_id = record.get("record_id", "")
        return job

    def create_deal(
        self,
        candidate_id: str,
        job_id: str,
        candidate_name: str,
        job_title: str,
        owner: str = ""
    ) -> Deal:
        """创建交易"""
        record = self.create_record("deals", {
            "候选人ID": candidate_id,
            "职位ID": job_id,
            "候选人姓名": candidate_name,
            "职位名称": job_title,
            "阶段": DealStage.NEW.value,
            "意向概率": 20,
            "负责顾问": owner
        })

        return Deal(
            record_id=record.get("record_id", ""),
            candidate_id=candidate_id,
            job_id=job_id,
            candidate_name=candidate_name,
            job_title=job_title,
            stage=DealStage.NEW,
            probability=20,
            owner=owner,
            created_at=datetime.now()
        )

    # ==================== Mock方法 ====================

    def _mock_get_records(self, table_name: str) -> List[Dict]:
        """Mock获取记录"""
        if table_name == "candidates":
            return [
                {
                    "record_id": "mock_cand_001",
                    "fields": {
                        "姓名": "张三",
                        "邮箱": "zhangsan@example.com",
                        "当前职位": "AI算法工程师",
                        "当前公司": "字节跳动",
                        "技能": ["Python", "TensorFlow", "PyTorch"],
                        "工作年限": 5,
                        "状态": "active"
                    }
                },
                {
                    "record_id": "mock_cand_002",
                    "fields": {
                        "姓名": "李四",
                        "邮箱": "lisi@example.com",
                        "当前职位": "产品经理",
                        "当前公司": "阿里巴巴",
                        "技能": ["产品设计", "数据分析", "用户研究"],
                        "工作年限": 7,
                        "状态": "interviewing"
                    }
                }
            ]
        elif table_name == "jobs":
            return [
                {
                    "record_id": "mock_job_001",
                    "fields": {
                        "职位名称": "AI算法专家",
                        "公司": "华为",
                        "所需技能": ["Python", "LLM", "PyTorch"],
                        "最低工作年限": 5,
                        "薪资下限": "80K",
                        "薪资上限": "150K",
                        "地点": "深圳",
                        "状态": "open"
                    }
                }
            ]
        elif table_name == "deals":
            return [
                {
                    "record_id": "mock_deal_001",
                    "fields": {
                        "候选人ID": "mock_cand_001",
                        "职位ID": "mock_job_001",
                        "候选人姓名": "张三",
                        "职位名称": "AI算法专家",
                        "阶段": "interview_scheduled",
                        "意向概率": 60,
                        "面试日期": (datetime.now() + timedelta(days=1)).isoformat(),
                        "负责顾问": "George"
                    }
                }
            ]

        return []

    def _mock_get_record(self, table_name: str, record_id: str) -> Dict:
        """Mock获取单条记录"""
        records = self._mock_get_records(table_name)
        for r in records:
            if r["record_id"] == record_id:
                return r
        return {"record_id": record_id, "fields": {}}

    def _mock_create_record(self, table_name: str, fields: Dict) -> Dict:
        """Mock创建记录"""
        return {
            "record_id": f"mock_new_{int(time.time())}",
            "fields": fields
        }

    def _mock_update_record(
        self,
        table_name: str,
        record_id: str,
        fields: Dict
    ) -> Dict:
        """Mock更新记录"""
        return {
            "record_id": record_id,
            "fields": fields
        }


# ============================================================
# 便捷函数
# ============================================================

def create_bitale_connector_from_config() -> BitableConnectorReal:
    """
    从配置文件创建Bitable连接器

    Returns:
        配置好的BitableConnectorReal实例
    """
    try:
        from config_bitables import (
            BITABLE_APP_ID,
            BITABLE_APP_SECRET,
            BITABLE_APP_TOKEN,
            TABLES,
            FIELD_MAPPING
        )
        return BitableConnectorReal(
            app_id=BITABLE_APP_ID,
            app_secret=BITABLE_APP_SECRET,
            app_token=BITABLE_APP_TOKEN,
            tables=TABLES,
            field_mapping=FIELD_MAPPING
        )
    except ImportError:
        print("[WARNING] config_bitables.py not found, using mock mode")
        return BitableConnectorReal()


# ============================================================
# 入口测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Bitable Connector - Real API Test")
    print("=" * 60)

    connector = create_bitale_connector_from_config()

    print(f"\nConnector mode: {'REAL API' if connector.app_id else 'MOCK'}")

    # 测试获取候选人
    print("\n[Test] Get Candidates")
    candidates = connector.get_candidates()
    print(f"  Found {len(candidates)} candidates")
    for c in candidates:
        print(f"  - {c.name} ({c.title} @ {c.company})")

    # 测试获取职位
    print("\n[Test] Get Jobs")
    jobs = connector.get_jobs()
    print(f"  Found {len(jobs)} jobs")
    for j in jobs:
        print(f"  - {j.title} @ {j.company} ({j.location})")

    # 测试获取交易
    print("\n[Test] Get Deals")
    deals = connector.get_deals()
    print(f"  Found {len(deals)} deals")
    for d in deals:
        print(f"  - {d.candidate_name} → {d.job_title} [{d.stage.value}]")

    # 测试创建候选人
    print("\n[Test] Create Candidate")
    new_cand = Candidate(
        name="王五",
        email="wangwu@example.com",
        title="数据科学家",
        company="腾讯",
        skills=["Python", "Machine Learning", "SQL"],
        experience_years=4
    )
    created = connector.create_candidate(new_cand)
    print(f"  Created: {created.name} (ID: {created.record_id})")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
