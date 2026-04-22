"""
职位模型 (Job Model)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class JobType(str, Enum):
    """职位类型"""
    FULL_TIME = "full_time"           # 全职
    PART_TIME = "part_time"           # 兼职
    CONTRACT = "contract"             # 合同制
    INTERNSHIP = "internship"         # 实习


class JobDifficulty(str, Enum):
    """匹配难度"""
    EASY = "easy"                     # 容易
    MEDIUM = "medium"                 # 中等
    HARD = "hard"                     # 困难


class JobBase(BaseModel):
    """职位基础模型"""
    title: str = Field(..., description="职位名称")
    company_name: str = Field(..., description="公司名称")
    location: str = Field(..., description="工作地点")
    salary_min: Optional[int] = Field(None, description="薪资下限")
    salary_max: Optional[int] = Field(None, description="薪资上限")


class JobCreate(JobBase):
    """职位创建模型"""
    job_type: JobType = Field(JobType.FULL_TIME, description="职位类型")
    description: Optional[str] = Field(None, description="职位描述原文")
    requirements: Optional[str] = Field(None, description="职位要求原文")
    department: Optional[str] = Field(None, description="部门")
    headcount: Optional[int] = Field(1, description="招聘人数")
    urgency: Optional[str] = Field("normal", description="紧急程度: urgent/high/normal/low")


class JDIntelligence(JobCreate):
    """JD智能画像模型 (v2.0)"""
    # 解析后的结构化字段
    required_skills: List[str] = Field(default_factory=list, description="必备技能")
    preferred_skills: List[str] = Field(default_factory=list, description="优先技能")
    min_experience_years: Optional[int] = Field(None, description="最低工作年限")
    education_requirement: Optional[str] = Field(None, description="学历要求")

    # 隐含偏好挖掘
    hidden_preferences: List[Dict[str, str]] = Field(default_factory=list, description="隐含偏好")

    # 超预期公司亮点
    company_highlights: List[Dict[str, Any]] = Field(default_factory=list, description="公司亮点")

    # 分析结果
    candidate_rarity: Optional[str] = Field(None, description="候选人稀缺性评估")
    salary_competitiveness: Optional[str] = Field(None, description="薪资竞争力")
    difficulty_rating: JobDifficulty = Field(JobDifficulty.MEDIUM, description="匹配难度")
    attraction_score: Optional[float] = Field(None, description="JD吸引力评分", ge=0, le=100)

    # 猎头推岗策略
    headhunting_strategy: Optional[Dict[str, Any]] = Field(None, description="推岗策略")


class Job(JDIntelligence):
    """完整职位模型"""
    id: str = Field(..., description="职位ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    created_by: str = Field(..., description="创建人")
    status: str = Field("open", description="状态: open/paused/closed")
    source: str = Field("manual", description="来源: manual/feishu/linkedin")


class JobResponse(BaseModel):
    """API响应模型"""
    success: bool = True
    data: Optional[Job] = None
    message: Optional[str] = None


class JobListResponse(BaseModel):
    """列表响应模型"""
    success: bool = True
    data: List[Job] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
