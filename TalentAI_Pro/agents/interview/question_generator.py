"""
Question Generator - 问题生成器

根据 JD 和候选人背景生成结构化面试问题
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class TechnicalQuestion:
    """技术问题"""
    id: str
    skill: str                    # 技能领域
    level: str                   # 难度级别: junior/mid/senior/expert
    question: str                # 问题文本
    expected_keywords: List[str] # 期望的关键词
    difficulty: int             # 1-5 难度
    category: str = "technical" # 问题类别

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "skill": self.skill,
            "level": self.level,
            "question": self.question,
            "expected_keywords": self.expected_keywords,
            "difficulty": self.difficulty,
            "category": self.category
        }


@dataclass
class BehavioralQuestion:
    """行为面试问题 (STAR法则)"""
    id: str
    category: str                # leadership/teamwork/problem_solving/communication
    question: str
    star_framework: bool = True
    category_cn: str = ""        # 中文类别名

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "question": self.question,
            "star_framework": self.star_framework,
            "category_cn": self.category_cn
        }


@dataclass
class StructuredQuestions:
    """结构化面试问题集"""
    interview_id: str
    technical_questions: List[TechnicalQuestion] = field(default_factory=list)
    behavioral_questions: List[BehavioralQuestion] = field(default_factory=list)
    duration_minutes: int = 60
    total_questions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "technical_questions": [q.to_dict() for q in self.technical_questions],
            "behavioral_questions": [q.to_dict() for q in self.behavioral_questions],
            "duration_minutes": self.duration_minutes,
            "total_questions": self.total_questions
        }


# 问题模板库
TECHNICAL_QUESTION_TEMPLATES = {
    "Python": {
        "junior": [
            {
                "question": "请解释Python中列表和元组的区别",
                "expected_keywords": ["可变", "不可变", "列表", "元组", "索引"],
                "difficulty": 1
            },
            {
                "question": "Python中的字典如何进行遍历？",
                "expected_keywords": ["keys()", "values()", "items()", "for循环"],
                "difficulty": 1
            }
        ],
        "mid": [
            {
                "question": "请解释Python中的装饰器(Decorator)是什么？如何使用？",
                "expected_keywords": ["函数", "嵌套", "@", "wrapper", "高阶函数"],
                "difficulty": 3
            },
            {
                "question": "Python中的生成器(Generator)和迭代器(Iterator)有什么区别？",
                "expected_keywords": ["yield", "__iter__", "__next__", "惰性计算", "内存"],
                "difficulty": 3
            }
        ],
        "senior": [
            {
                "question": "请解释Python中的GIL(全局解释器锁)是什么，以及它对多线程的影响？",
                "expected_keywords": ["Global Interpreter Lock", "线程安全", "并行", "多进程", "异步"],
                "difficulty": 4
            },
            {
                "question": "Python中的内存管理机制是怎样的？如何排查内存泄漏？",
                "expected_keywords": ["引用计数", "垃圾回收", "循环引用", "memory_profiler", "tracemalloc"],
                "difficulty": 4
            }
        ],
        "expert": [
            {
                "question": "请设计一个Python异步框架的核心组件，并解释其实现原理",
                "expected_keywords": ["event_loop", "coroutine", "async/await", "future", "任务调度"],
                "difficulty": 5
            }
        ]
    },
    "JavaScript": {
        "junior": [
            {
                "question": "JavaScript中的var、let、const有什么区别？",
                "expected_keywords": ["作用域", "变量提升", "暂时性死区", "常量"],
                "difficulty": 1
            }
        ],
        "mid": [
            {
                "question": "解释JavaScript中的闭包(Closure)是什么？有什么应用场景？",
                "expected_keywords": ["函数", "作用域", "词法环境", "私有变量", "回调"],
                "difficulty": 3
            }
        ],
        "senior": [
            {
                "question": "JavaScript的事件循环(Event Loop)是如何工作的？setTimeout和Promise的执行顺序？",
                "expected_keywords": ["调用栈", "任务队列", "微任务", "宏任务", "async"],
                "difficulty": 4
            }
        ],
        "expert": [
            {
                "question": "请解释JavaScript引擎(V8)如何优化代码执行？",
                "expected_keywords": ["JIT", "隐藏类", "内联缓存", "逃逸分析", "TurboFan"],
                "difficulty": 5
            }
        ]
    },
    "React": {
        "junior": [
            {
                "question": "React中的Props和State有什么区别？",
                "expected_keywords": ["不可变", "可读", "组件", "渲染"],
                "difficulty": 1
            }
        ],
        "mid": [
            {
                "question": "React中的Hook是什么？useEffect的使用注意事项？",
                "expected_keywords": ["useState", "useEffect", "依赖数组", "清理函数", "副作用"],
                "difficulty": 3
            }
        ],
        "senior": [
            {
                "question": "React的Fiber架构是什么？如何实现增量渲染？",
                "expected_keywords": ["Fiber", "reconciliation", "workLoop", "优先级", "suspense"],
                "difficulty": 4
            }
        ],
        "expert": [
            {
                "question": "如何设计一个高性能的React状态管理方案？",
                "expected_keywords": ["状态切片", "选择器", "派生状态", "缓存", "性能优化"],
                "difficulty": 5
            }
        ]
    }
}

BEHAVIORAL_QUESTION_TEMPLATES = {
    "leadership": {
        "question": "请描述一次你带领团队克服重大技术挑战的经历。你是如何组织团队并最终解决问题的？",
        "category_cn": "领导力"
    },
    "teamwork": {
        "question": "描述一次你与团队成员意见不合的经历。你是如何处理的？结果如何？",
        "category_cn": "团队协作"
    },
    "problem_solving": {
        "question": "讲述一次你在项目中遇到紧急问题的经历。你是如何快速响应并解决的？",
        "category_cn": "问题解决"
    },
    "communication": {
        "question": "描述一次你需要向非技术背景的人解释复杂技术问题的经历。你是如何确保对方理解的？",
        "category_cn": "沟通表达"
    },
    "growth": {
        "question": "请分享一个你在技术上快速成长的经历。你是如何学习的？有什么方法可以分享吗？",
        "category_cn": "成长潜力"
    },
    "failure": {
        "question": "请描述一次失败的项目或经历。你从中学到了什么？",
        "category_cn": "失败与复盘"
    }
}


class QuestionGenerator:
    """
    面试问题生成器

    根据职位要求(JD)和候选人背景生成针对性的面试问题
    """

    def __init__(self):
        self.technical_templates = TECHNICAL_QUESTION_TEMPLATES
        self.behavioral_templates = BEHAVIORAL_QUESTION_TEMPLATES

    def generate(
        self,
        job_description: Dict[str, Any],
        candidate_profile: Dict[str, Any]
    ) -> StructuredQuestions:
        """
        生成结构化面试问题

        Args:
            job_description: JD解析结果，包含 skills, level, requirements 等
            candidate_profile: 候选人背景，包含 skills, experience_years 等

        Returns:
            StructuredQuestions: 结构化问题集
        """
        interview_id = str(uuid.uuid4())

        # 提取关键信息
        required_skills = job_description.get("skills", [])
        job_level = job_description.get("level", "mid")
        candidate_skills = candidate_profile.get("skills", [])
        candidate_experience = candidate_profile.get("experience_years", 0)

        # 生成技术问题
        technical_questions = self._generate_technical_questions(
            required_skills, job_level
        )

        # 生成行为问题
        behavioral_questions = self._generate_behavioral_questions()

        # 计算面试时长
        duration = self._calculate_duration(
            len(technical_questions),
            len(behavioral_questions)
        )

        questions = StructuredQuestions(
            interview_id=interview_id,
            technical_questions=technical_questions,
            behavioral_questions=behavioral_questions,
            duration_minutes=duration,
            total_questions=len(technical_questions) + len(behavioral_questions)
        )

        return questions

    def _generate_technical_questions(
        self,
        skills: List[str],
        level: str
    ) -> List[TechnicalQuestion]:
        """根据技能生成技术问题"""
        questions = []
        question_id_prefix = str(uuid.uuid4())[:8]

        for i, skill in enumerate(skills):
            skill_upper = skill.title() if skill.lower() in ["python", "javascript", "react"] else skill.capitalize()

            if skill_upper in self.technical_templates:
                # 从模板库获取
                level_questions = self.technical_templates[skill_upper].get(level, [])
                for j, q_template in enumerate(level_questions[:2]):  # 每个技能最多2题
                    questions.append(TechnicalQuestion(
                        id=f"{question_id_prefix}-t-{i}-{j}",
                        skill=skill,
                        level=level,
                        question=q_template["question"],
                        expected_keywords=q_template["expected_keywords"],
                        difficulty=q_template["difficulty"]
                    ))
            else:
                # 生成通用问题
                questions.append(TechnicalQuestion(
                    id=f"{question_id_prefix}-t-{i}-0",
                    skill=skill,
                    level=level,
                    question=f"请详细解释{skill}的核心概念和原理",
                    expected_keywords=[skill],
                    difficulty=3
                ))

        return questions

    def _generate_behavioral_questions(self) -> List[BehavioralQuestion]:
        """生成行为面试问题"""
        questions = []
        question_id_prefix = str(uuid.uuid4())[:8]

        categories = list(self.behavioral_templates.keys())
        for i, category in enumerate(categories):
            template = self.behavioral_templates[category]
            questions.append(BehavioralQuestion(
                id=f"{question_id_prefix}-b-{i}",
                category=category,
                question=template["question"],
                star_framework=True,
                category_cn=template["category_cn"]
            ))

        return questions

    def _calculate_duration(
        self,
        num_technical: int,
        num_behavioral: int
    ) -> int:
        """计算面试时长（分钟）"""
        # 技术问题：平均5分钟/题
        # 行为问题：平均8分钟/题
        # 预留10分钟开场和5分钟反问
        duration = num_technical * 5 + num_behavioral * 8 + 15
        return min(duration, 120)  # 最多120分钟


# 便捷函数
def generate_interview_questions(
    job_description: Dict[str, Any],
    candidate_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    生成面试问题的便捷函数

    Args:
        job_description: JD解析结果
        candidate_profile: 候选人背景

    Returns:
        包含问题列表的字典
    """
    generator = QuestionGenerator()
    questions = generator.generate(job_description, candidate_profile)
    return questions.to_dict()