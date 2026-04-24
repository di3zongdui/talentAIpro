"""
Interview Preparer
Helps candidates prepare for interviews
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import random


@dataclass
class InterviewQuestion:
    """Interview question with tips"""
    question: str
    question_type: str  # behavioral, technical, situational
    tips: List[str]
    sample_answer: Optional[str] = None


class InterviewPreparer:
    """
    Interview preparation assistant

    Features:
    - Company research
    - Question bank generation
    - Answer structuring (STAR)
    - Mock interview simulation
    - Feedback and improvement
    """

    # Question templates by category
    QUESTION_TEMPLATES = {
        "behavioral": [
            "请描述一次你在项目中遇到最大挑战的经历。",
            "讲述一个你需要同时处理多个紧急任务的经历。",
            "分享一次你与团队成员产生分歧如何解决的经历。",
            "描述一个你主动承担责任解决团队问题的例子。",
        ],
        "technical": {
            "Python": [
                "Python中的GIL是什么？它如何影响多线程编程？",
                "请解释装饰器(Decorator)的工作原理。",
                "Python中生成器和迭代器的区别是什么？",
            ],
            "System Design": [
                "如何设计一个高可用的系统？",
                "描述如何设计一个URL缩短服务。",
                "如何处理系统中的缓存失效问题？",
            ],
        },
        "situational": [
            "如果你发现同事提交了有问题的代码，你会怎么做？",
            "如果项目进度落后于计划，你会如何应对？",
            "如果产品需求不明确，你会怎么做？",
        ],
    }

    # STAR components
    STAR_COMPONENTS = [
        ("Situation", "背景", "项目的背景是什么？你面临什么情况？"),
        ("Task", "任务", "你的职责是什么？需要完成什么目标？"),
        ("Action", "行动", "你具体采取了什么行动？"),
        ("Result", "结果", "最终结果如何？你学到了什么？"),
    ]

    def __init__(self):
        self._preparation_sessions: Dict[str, Dict[str, Any]] = {}

    def create_preparation(self, job: Dict[str, Any],
                          candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive interview preparation

        job: Job details including skills, company info
        candidate_profile: Candidate's background and experience
        """
        session_id = f"prep_{len(self._preparation_sessions) + 1}"

        preparation = {
            "session_id": session_id,
            "company_research": self._research_company(job.get("company", "")),
            "questions": self._generate_questions(job, candidate_profile),
            "star_guide": self._get_star_guide(),
            "salary_guide": self._generate_salary_guide(job),
            "questions_to_ask": self._generate_interviewer_questions(job),
            "status": "ready",
        }

        self._preparation_sessions[session_id] = preparation
        return preparation

    def _research_company(self, company: str) -> Dict[str, Any]:
        """Research company for interview"""
        # In production, would call web search
        return {
            "name": company,
            "industry": "Technology / Internet",
            "company_size": "1000-5000人",
            "stage": "成长期",
            "products": ["核心产品A", "核心产品B"],
            "culture": "工程师文化，注重技术分享和持续学习",
            "recent_news": "近期完成D轮融资",
            "mission": "用技术改变生活",
        }

    def _generate_questions(self, job: Dict[str, Any],
                           profile: Dict[str, Any]) -> List[InterviewQuestion]:
        """Generate relevant interview questions"""
        questions = []
        skills = job.get("skills", [])
        experience = profile.get("experience_years", 0)

        # Behavioral questions (always ask)
        for q in self.QUESTION_TEMPLATES["behavioral"]:
            questions.append(InterviewQuestion(
                question=q,
                question_type="behavioral",
                tips=[
                    "使用STAR方法组织答案",
                    "选择能体现你技能的案例",
                    "量化你的成果（如：提升性能30%）",
                ],
            ))

        # Technical questions based on skills
        for skill in skills[:3]:  # Top 3 skills
            tech_questions = self.QUESTION_TEMPLATES["technical"].get(skill, [])
            for q in tech_questions[:2]:  # 2 questions per skill
                questions.append(InterviewQuestion(
                    question=q,
                    question_type="technical",
                    tips=[
                        "先解释概念",
                        "举实际例子",
                        "如果有优化方案，说出来",
                    ],
                ))

        # Situational questions
        for q in self.QUESTION_TEMPLATES["situational"]:
            questions.append(InterviewQuestion(
                question=q,
                question_type="situational",
                tips=[
                    "展示你的问题解决能力",
                    "强调团队协作精神",
                    "说明你的决策过程",
                ],
            ))

        return questions

    def _get_star_guide(self) -> Dict[str, Any]:
        """Get STAR method guide"""
        return {
            "title": "STAR法则",
            "description": "结构化回答行为面试问题的方法",
            "components": [
                {
                    "letter": "S",
                    "name": "Situation",
                    "chinese": "情境",
                    "description": "描述项目或任务的背景环境",
                    "example": "在我上一份工作中，我们团队需要在一个月的时间内开发一个新的用户认证系统...",
                    "tips": [
                        "简洁明了，30秒内完成",
                        "提供足够的上下文",
                        "让面试官理解你的角色",
                    ],
                },
                {
                    "letter": "T",
                    "name": "Task",
                    "chinese": "任务",
                    "description": "明确你的职责和目标",
                    "example": "作为后端工程师，我负责设计数据库结构和API接口...",
                    "tips": [
                        "清晰定义你的具体任务",
                        "说明目标是什么",
                    ],
                },
                {
                    "letter": "A",
                    "name": "Action",
                    "chinese": "行动",
                    "description": "你具体做了什么",
                    "example": "我首先分析了现有系统的瓶颈，然后设计了新的数据库架构，使用Redis缓存来提升性能...",
                    "tips": [
                        "重点描述你的贡献",
                        "使用'action verbs'(设计、开发、优化)',
                        "展示你的技术能力",
                    ],
                },
                {
                    "letter": "R",
                    "name": "Result",
                    "chinese": "结果",
                    "description": "最终成果和你学到什么",
                    "example": "系统响应时间从2秒降低到200毫秒，用户满意度提升25%，我也在这个过程中学习了高并发系统设计...",
                    "tips": [
                        "尽可能量化结果",
                        "用数据说话",
                        "反思学到的经验",
                    ],
                },
            ],
        }

    def _generate_salary_guide(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Generate salary negotiation guide"""
        job_salary_min = job.get("salary_min", 0)
        job_salary_max = job.get("salary_max", 0)

        return {
            "market_range": {
                "min": int(job_salary_min * 0.9),
                "mid": int((job_salary_min + job_salary_max) / 2),
                "max": int(job_salary_max * 1.1),
            },
            "negotiation_tips": [
                {
                    "phase": "等待时机",
                    "tip": "等待面试官先提出薪资问题",
                    "when": "第一轮/第二轮面试",
                },
                {
                    "phase": "了解范围",
                    "tip": "询问该职位的薪资范围",
                    "when": "面试官提出薪资问题时",
                },
                {
                    "phase": "提供锚点",
                    "tip": "基于市场数据提出期望",
                    "when": "被问及期望薪资时",
                },
                {
                    "phase": "考虑总包",
                    "tip": "除了基本工资，还要谈奖金、期权、福利",
                    "when": "讨论offer时",
                },
            ],
            "phrases": {
                "decline": "我对这个薪资有些顾虑...",
                "counter": "基于我的经验和市场数据，我期望...",
                "accept": "这个offer整体符合我的期望，我愿意接受",
            },
        }

    def _generate_interviewer_questions(self, job: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate questions to ask the interviewer"""
        return [
            {
                "category": "团队",
                "question": "团队的技术栈是什么？",
                "purpose": "了解实际工作环境",
            },
            {
                "category": "团队",
                "question": "团队有多少人？如何分工？",
                "purpose": "了解团队结构",
            },
            {
                "category": "成长",
                "question": "入职后前3个月的预期是什么？",
                "purpose": "了解老板期望",
            },
            {
                "category": "成长",
                "question": "工程师有哪些学习和发展机会？",
                "purpose": "了解公司对工程师成长的投入",
            },
            {
                "category": "文化",
                "question": "团队如何做code review？",
                "purpose": "了解代码质量标准和协作方式",
            },
            {
                "category": "文化",
                "question": "加班文化如何？工作生活平衡吗？",
                "purpose": "了解工作节奏",
            },
            {
                "category": "流程",
                "question": "绩效考核的标准是什么？",
                "purpose": "了解评估体系",
            },
        ]

    def simulate_answer(self, question: InterviewQuestion,
                       answer: str) -> Dict[str, Any]:
        """
        Simulate evaluation of an interview answer

        Returns feedback and scores
        """
        # Simplified evaluation
        word_count = len(answer)
        has_numbers = any(c.isdigit() for c in answer)
        has_star_keywords = any(kw in answer for kw in ["首先", "然后", "最终", "结果", "我", "我们"])

        # Calculate scores
        scores = {
            "structure": 0.6 if has_star_keywords else 0.3,
            "specificity": 0.7 if has_numbers else 0.4,
            "completeness": min(1.0, word_count / 200),
            "relevance": 0.7,  # Simplified
        }

        overall = sum(scores.values()) / len(scores)

        # Generate feedback
        feedback = []
        if scores["structure"] < 0.5:
            feedback.append("建议使用STAR方法组织答案")
        if scores["specificity"] < 0.5:
            feedback.append("可以添加更多具体数据和细节")
        if scores["completeness"] < 0.5:
            feedback.append("答案可以更详细一些，建议200字以上")
        if overall >= 0.7:
            feedback.append("回答得很好！继续保持")

        return {
            "question": question.question,
            "answer_length": word_count,
            "scores": {k: round(v, 2) for k, v in scores.items()},
            "overall_score": round(overall, 2),
            "feedback": feedback,
            "suggestions": self._improve_answer_suggestions(question, answer),
        }

    def _improve_answer_suggestions(self, question: InterviewQuestion,
                                   answer: str) -> List[str]:
        """Generate suggestions to improve answer"""
        suggestions = []

        if question.question_type == "behavioral":
            suggestions.append("确保你的回答展示了你的技能而非仅仅是团队的成绩")
            suggestions.append("用具体的数字来量化成果（如效率提升X%）")

        if question.question_type == "technical":
            suggestions.append("可以先解释基本概念，再举实际例子")
            suggestions.append("如果知道最佳实践，可以提到")

        return suggestions
