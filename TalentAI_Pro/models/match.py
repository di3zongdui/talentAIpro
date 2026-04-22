"""
匹配结果模型 (Match Model)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MatchConfidence(str, Enum):
    """匹配置信度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MatchScore(BaseModel):
    """匹配评分模型"""
    base_score: float = Field(..., description="基础匹配分", ge=0, le=100)
    surprise_score: Optional[float] = Field(0, description="超预期惊喜分", ge=0, le=20)
    final_score: float = Field(..., description="最终匹配分", ge=0, le=100)

    # 双向满意分
    recruiter_satisfaction: float = Field(..., description="招聘者满意分", ge=0, le=100)
    candidate_satisfaction: float = Field(..., description="候选人满意分", ge=0, le=100)

    # 匹配详情
    skill_match_details: Dict[str, float] = Field(default_factory=dict, description="技能匹配详情")
    experience_match: float = Field(0, description="经验匹配分", ge=0, le=100)
    location_match: float = Field(0, description="地点匹配分", ge=0, le=100)
    salary_match: float = Field(0, description="薪资匹配分", ge=0, le=100)

    # 置信度
    confidence: MatchConfidence = Field(MatchConfidence.MEDIUM, description="置信度")


class MatchResult(BaseModel):
    """匹配结果模型"""
    id: str = Field(..., description="匹配ID")
    job_id: str = Field(..., description="职位ID")
    candidate_id: str = Field(..., description="候选人ID")

    # 匹配评分
    score: MatchScore = Field(..., description="匹配评分")

    # 超预期亮点（从Discovery Radar获取）
    candidate_surprise_highlights: List[Dict[str, Any]] = Field(
        default_factory=list, description="候选人超预期亮点"
    )
    company_surprise_highlights: List[Dict[str, Any]] = Field(
        default_factory=list, description="公司超预期亮点"
    )

    # 触发条件
    commitment_triggered: bool = Field(False, description="是否触发承诺机制(>=75%)")
    recruiter_threshold_met: bool = Field(False, description="招聘者阈值是否满足")
    candidate_threshold_met: bool = Field(False, description="候选人阈值是否满足")

    # 撮合综合分
    # 综合撮合分 = 招聘者满意分 × √(候选人满意分)
    composite_score: float = Field(0, description="综合撮合分", ge=0, le=100)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="匹配时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 状态
    status: str = Field("pending", description="状态: pending/contacted/interviewing/offered/closed")

    # 推荐理由
    recommendation_reason: Optional[str] = Field(None, description="推荐理由")
    risk_warnings: List[str] = Field(default_factory=list, description="风险提示")


class MatchListResponse(BaseModel):
    """匹配列表响应"""
    success: bool = True
    data: List[MatchResult] = Field(default_factory=list)
    total: int = 0
    top_matches: List[MatchResult] = Field(default_factory=list, description="最优匹配列表")


class MatchResponse(BaseModel):
    """单条匹配响应"""
    success: bool = True
    data: Optional[MatchResult] = None
    message: Optional[str] = None
