"""
Interview Agent - 面试Agent
替代面试官执行结构化面试

核心功能:
- 技术问题生成
- 行为面试问题 (STAR法则)
- 实时评估与评分
- 结构化反馈报告
"""

from .question_generator import QuestionGenerator
from .evaluation_engine import EvaluationEngine
from .report_generator import ReportGenerator
from .interview_session import InterviewSession, InterviewSessionManager, InterviewType

__all__ = [
    "QuestionGenerator",
    "EvaluationEngine",
    "ReportGenerator",
    "InterviewSession",
    "InterviewSessionManager",
    "InterviewType",
]

# Interview Agent 状态
class InterviewState:
    """面试状态枚举"""
    CREATED = "created"                          # 创建
    QUESTIONS_GENERATED = "questions_generated"   # 问题已生成
    IN_PROGRESS = "in_progress"                  # 进行中
    COMPLETED = "completed"                      # 已完成
    CANCELLED = "cancelled"                      # 已取消

# 评估维度定义
EVALUATION_DIMENSIONS = {
    "technical_depth": {
        "name": "技术深度",
        "description": "对技术概念的深入理解",
        "weight": 0.30,
        "levels": {
            1: "了解基础概念",
            2: "能正确使用，有一定理解",
            3: "理解原理，能举一反三",
            4: "深入理解，知晓最佳实践",
            5: "专家级别，知晓底层实现"
        }
    },
    "problem_solving": {
        "name": "问题解决",
        "description": "分析和解决问题的能力",
        "weight": 0.25,
        "levels": {
            1: "需要较多指导",
            2: "能解决常见问题",
            3: "能独立解决中等难度问题",
            4: "能解决复杂问题，有系统性方法",
            5: "能解决未知领域问题"
        }
    },
    "communication": {
        "name": "沟通表达",
        "description": "清晰表达想法的能力",
        "weight": 0.20,
        "levels": {
            1: "表达混乱，难以理解",
            2: "基本能表达想法",
            3: "表达清晰，逻辑较好",
            4: "表达流畅，逻辑严密",
            5: "表达卓越，具有影响力"
        }
    },
    "culture_fit": {
        "name": "文化匹配",
        "description": "与团队文化的契合度",
        "weight": 0.15,
        "levels": {
            1: "价值观差异较大",
            2: "基本匹配",
            3: "匹配度较高",
            4: "高度匹配",
            5: "完美契合"
        }
    },
    "growth_potential": {
        "name": "成长潜力",
        "description": "学习和发展潜力",
        "weight": 0.10,
        "levels": {
            1: "成长有限",
            2: "有一定成长空间",
            3: "成长空间良好",
            4: "很大成长空间",
            5: "无限潜力"
        }
    }
}

# 推荐级别定义
RECOMMENDATION_LEVELS = {
    (4.5, 5.0): "强烈推荐",
    (4.0, 4.5): "推荐",
    (3.5, 4.0): "可以考虑",
    (3.0, 3.5): "谨慎考虑",
    (0.0, 3.0): "不推荐"
}