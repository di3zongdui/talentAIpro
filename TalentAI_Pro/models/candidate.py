"""
候选人模型 (Candidate Model)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class WorkStyle(str, Enum):
    """工作风格"""
    TECHNICAL = "technical"           # 技术型
    COMMERCIAL = "commercial"         # 商业型
    ACADEMIC = "academic"             # 学术型
    ENTREPRENEURIAL = "entrepreneurial" # 创业型


class CandidateBase(BaseModel):
    """候选人基础模型"""
    name: str = Field(..., description="候选人姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    location: Optional[str] = Field(None, description="所在地")
    current_title: Optional[str] = Field(None, description="当前职位")
    current_company: Optional[str] = Field(None, description="当前公司")


class CandidateCreate(CandidateBase):
    """候选人创建模型"""
    resume_text: Optional[str] = Field(None, description="简历文本")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn URL")
    github_url: Optional[str] = Field(None, description="GitHub URL")
    expected_salary_min: Optional[int] = Field(None, description="期望薪资下限")
    expected_salary_max: Optional[int] = Field(None, description="期望薪资上限")
    preferred_locations: Optional[List[str]] = Field(default_factory=list, description="偏好地点")
    preferred_job_titles: Optional[List[str]] = Field(default_factory=list, description="偏好职位")


class CandidateIntelligence(CandidateBase):
    """候选人智能画像模型 (v2.0)"""
    # 基础信息
    years_of_experience: int = Field(0, description="工作年限")
    education_level: Optional[str] = Field(None, description="学历")
    education_school: Optional[str] = Field(None, description="毕业院校")

    # 全网背景补充
    linkedin_data: Optional[Dict[str, Any]] = Field(None, description="LinkedIn数据")
    github_data: Optional[Dict[str, Any]] = Field(None, description="GitHub数据")
    xiaomai_data: Optional[Dict[str, Any]] = Field(None, description="脉脉数据")
    paper_patent_data: Optional[Dict[str, Any]] = Field(None, description="论文/专利数据")

    # 超预期亮点
    surprise_highlights: List[Dict[str, Any]] = Field(default_factory=list, description="超预期亮点清单")
    risk_warnings: List[str] = Field(default_factory=list, description="风险预警")

    # 分析结果
    estimated_salary: Optional[int] = Field(None, description="估算薪资")
    estimated_level: Optional[str] = Field(None, description="估算职级")
    job_intent_prediction: Optional[str] = Field(None, description="求职意向推测")
    culture_fit_score: Optional[float] = Field(None, description="文化契合度", ge=0, le=1)

    # 工作风格
    work_style: Optional[WorkStyle] = Field(None, description="工作风格")


class Candidate(CandidateIntelligence):
    """完整候选人模型"""
    id: str = Field(..., description="候选人ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    source: str = Field("manual", description="来源: manual/linkedin/github/feishu")
    status: str = Field("active", description="状态: active/in_watch_pool/matched/closed")


class CandidateResponse(BaseModel):
    """API响应模型"""
    success: bool = True
    data: Optional[Candidate] = None
    message: Optional[str] = None


class CandidateListResponse(BaseModel):
    """列表响应模型"""
    success: bool = True
    data: List[Candidate] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
