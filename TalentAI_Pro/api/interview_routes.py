"""
面试评估 API - 智能面试评估
============================

提供智能面试评估功能：
- 基于简历+职位+回答，LLM生成个性化评估报告
- 多维度评分（技术力、沟通力、文化匹配等）
- 生成追问建议和提升建议
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/interview", tags=["Interview"])


# ========== 数据模型 ==========

class IntelligentEvaluationRequest(BaseModel):
    """智能评估请求"""
    candidate_name: str
    candidate_resume: str  # 候选人简历/背景
    job_title: str  # 职位名称
    job_requirements: List[str]  # 职位要求
    job_description: Optional[str] = None  # 职位描述
    questions: List[str]  # 面试问题列表
    answers: List[str]  # 候选人回答列表
    interview_context: Optional[str] = None  # 面试场景补充


class EvaluationDimension(BaseModel):
    """评估维度"""
    name: str
    score: float  # 0-100
    level: str  # "excellent" / "good" / "average" / "poor"
    evidence: List[str]  # 评分依据
    suggestions: List[str]  # 提升建议


class InterviewEvaluationResponse(BaseModel):
    """面试评估响应"""
    session_id: str
    overall_score: float  # 综合评分 0-100
    overall_level: str  # overall level
    dimensions: List[EvaluationDimension]  # 各维度评分
    strengths: List[str]  # 核心优势
    weaknesses: List[str]  # 不足之处
    recommended_questions: List[str]  # 建议追问
    final_verdict: str  # 最终录用建议
    detailed_report: str  # 详细评估报告


# ========== 存储 ==========

_evaluations: Dict[str, Dict[str, Any]] = {}


# ========== API ==========

@router.post("/intelligent-evaluation", response_model=InterviewEvaluationResponse)
async def intelligent_evaluation(request: IntelligentEvaluationRequest) -> Dict[str, Any]:
    """
    智能面试评估

    基于简历、职位要求、问答内容，生成个性化评估报告。

    评估维度：
    - 技术能力 (technical)
    - 沟通表达 (communication)
    - 问题解决 (problem_solving)
    - 文化匹配 (culture_fit)
    - 潜力可塑性 (growth_potential)
    """
    from api.llm_routes import get_gateway
    gateway = get_gateway()

    # 确保Provider已配置
    if not gateway._providers:
        raise HTTPException(status_code=400, detail="No provider configured. Please call /api/llm/configure first.")

    # 构建评估提示词
    evaluation_prompt = f"""你是专业的面试评估专家，请对候选人的面试表现进行全面评估。

## 候选人信息
姓名: {request.candidate_name}
简历/背景:
{request.candidate_resume}

## 职位信息
职位: {request.job_title}
职位要求: {', '.join(request.job_requirements)}
职位描述: {request.job_description or '暂无详细描述'}

## 面试问答记录
"""

    for i, (q, a) in enumerate(zip(request.questions, request.answers), 1):
        evaluation_prompt += f"\n问题{i}: {q}\n回答{i}: {a}\n"

    if request.interview_context:
        evaluation_prompt += f"\n面试场景补充: {request.interview_context}\n"

    evaluation_prompt += """
请返回JSON格式的详细评估报告：

{
    "overall_score": 85,  // 综合评分 0-100
    "overall_level": "good",  // excellent/good/average/poor

    "dimensions": [
        {
            "name": "技术能力",
            "score": 88,  // 0-100
            "level": "excellent",  // excellent/good/average/poor
            "evidence": ["面试回答展示了扎实的算法基础", "能清晰解释设计方案"],
            "suggestions": ["可以加强分布式系统设计能力"]
        }
    ],

    "strengths": [
        "技术基础扎实，能举一反三",
        "沟通表达清晰，逻辑性强"
    ],

    "weaknesses": [
        "缺乏大型项目经验",
        "对某些新技术了解不够深入"
    ],

    "recommended_questions": [
        "能描述一个你解决过的最具挑战性的技术问题吗？",
        "你如何保持对新技术的学习？"
    ],

    "final_verdict": "建议录用（有条件）",  // 强烈建议/建议/考虑/不建议录用

    "detailed_report": "详细评估报告的完整文本..."
}

请确保评估客观公正，基于实际问答内容给出评分和建议。
"""

    try:
        # 调用LLM进行评估
        model_key = "Qwen/Qwen3-Omni-30B-A3B-Instruct"
        response = await gateway.chat(prompt=evaluation_prompt, model=model_key)

        # 解析JSON响应
        import json
        import re

        def extract_json(text: str) -> dict:
            """从文本中提取JSON"""
            # 尝试匹配 {...} 格式
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {}

        evaluation_data = extract_json(response.content)

        # 如果解析失败，返回默认结构
        if not evaluation_data:
            evaluation_data = {
                "overall_score": 70,
                "overall_level": "average",
                "dimensions": [],
                "strengths": ["评估解析失败"],
                "weaknesses": ["无法从LLM响应中提取评估数据"],
                "recommended_questions": [],
                "final_verdict": "需要人工复评",
                "detailed_report": response.content[:500]
            }

        # 构建评估维度对象
        dimensions = []
        for dim in evaluation_data.get("dimensions", []):
            dimensions.append(EvaluationDimension(
                name=dim.get("name", "未知维度"),
                score=dim.get("score", 50),
                level=dim.get("level", "average"),
                evidence=dim.get("evidence", []),
                suggestions=dim.get("suggestions", [])
            ))

        # 生成session_id并存储
        session_id = f"interview-{uuid.uuid4().hex[:12]}"

        evaluation_record = {
            "session_id": session_id,
            "candidate_name": request.candidate_name,
            "job_title": request.job_title,
            "overall_score": evaluation_data.get("overall_score", 0),
            "overall_level": evaluation_data.get("overall_level", "unknown"),
            "dimensions": [d.model_dump() for d in dimensions],
            "final_verdict": evaluation_data.get("final_verdict", "待定"),
            "created_at": datetime.now().isoformat()
        }
        _evaluations[session_id] = evaluation_record

        return {
            "success": True,
            "session_id": session_id,
            "overall_score": evaluation_data.get("overall_score", 0),
            "overall_level": evaluation_data.get("overall_level", "unknown"),
            "dimensions": dimensions,
            "strengths": evaluation_data.get("strengths", []),
            "weaknesses": evaluation_data.get("weaknesses", []),
            "recommended_questions": evaluation_data.get("recommended_questions", []),
            "final_verdict": evaluation_data.get("final_verdict", "待定"),
            "detailed_report": evaluation_data.get("detailed_report", response.content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能评估失败: {str(e)}")


@router.get("/evaluation/{session_id}")
async def get_evaluation(session_id: str) -> Dict[str, Any]:
    """获取评估结果"""
    if session_id not in _evaluations:
        raise HTTPException(status_code=404, detail="评估记录不存在")

    return {
        "success": True,
        "data": _evaluations[session_id]
    }


@router.get("/evaluations")
async def list_evaluations(limit: int = 10) -> Dict[str, Any]:
    """列出最近的评估记录"""
    evaluations = list(_evaluations.values())
    evaluations.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {
        "success": True,
        "data": evaluations[:limit],
        "total": len(evaluations)
    }
