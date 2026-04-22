"""
JD Parser - 职位描述解析器

功能：
1. 文本解析 → 结构化字段
2. 隐含偏好挖掘
3. 薪资竞争力校准（待实现）
4. 匹配难度评级（待实现）
"""
from typing import Dict, List, Any, Optional
import re


class JDParser:
    """JD解析器"""

    # 常见技能关键词
    SKILL_KEYWORDS = [
        "Python", "Java", "Go", "Rust", "C++", "JavaScript", "TypeScript",
        "React", "Vue", "Angular", "Node.js", "Django", "FastAPI", "Spring",
        "AWS", "Azure", "GCP", "Kubernetes", "Docker", "Linux",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis",
        "Agile", "Scrum", "DevOps", "CI/CD",
        "Leadership", "Management", "Strategy",
    ]

    # 隐含偏好映射
    HIDDEN_PREFERENCE_PATTERNS = {
        r"创业心态": "能接受低薪高股/高风险/一人多岗",
        r"从0到1": "需要有创业公司/从0搭建经验",
        r"快速成长": "接受高强度工作/频繁出差",
        r"技术热情": "对技术有深度追求，能持续学习",
        r"跨团队": "沟通能力强，能协调多方资源",
        r"独立完成": "能独当一面，不需要太多指导",
        r"大厂经验": "流程规范，但可能缺乏创业经验",
        r"海归": "英语好，国际视野，但成本高",
    }

    def __init__(self):
        self.raw_text = ""
        self.parsed_data = {}

    def parse(self, jd_text: str) -> Dict[str, Any]:
        """
        解析JD文本

        Args:
            jd_text: JD原文

        Returns:
            解析后的结构化数据
        """
        self.raw_text = jd_text

        # 1. 提取结构化字段
        skills = self._extract_skills(jd_text)
        experience = self._extract_experience(jd_text)
        education = self._extract_education(jd_text)

        # 2. 挖掘隐含偏好
        hidden_prefs = self._extract_hidden_preferences(jd_text)

        # 3. 构建结果
        result = {
            "raw_text": jd_text,
            "required_skills": skills["required"],
            "preferred_skills": skills["preferred"],
            "min_experience_years": experience,
            "education_requirement": education,
            "hidden_preferences": hidden_prefs,
            "salary_range": self._extract_salary_range(jd_text),
            "location": self._extract_location(jd_text),
        }

        self.parsed_data = result
        return result

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """提取技能"""
        required = []
        preferred = []

        text_lower = text.lower()

        for skill in self.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                if "优先" in text or "加分" in text or "更好" in text:
                    preferred.append(skill)
                else:
                    required.append(skill)

        return {"required": list(set(required)), "preferred": list(set(preferred))}

    def _extract_experience(self, text: str) -> Optional[int]:
        """提取工作年限要求"""
        patterns = [
            r"(\d+)\+?\s*年",
            r"(\d+)\s*年以上",
            r"经验\s*(\d+)\s*年",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        return None

    def _extract_education(self, text: str) -> Optional[str]:
        """提取学历要求"""
        education_levels = ["博士", "硕士", "研究生", "本科", "学士", "大专", "高中"]

        for level in education_levels:
            if level in text:
                return level

        return None

    def _extract_hidden_preferences(self, text: str) -> List[Dict[str, str]]:
        """挖掘隐含偏好"""
        hidden = []

        for keyword, meaning in self.HIDDEN_PREFERENCE_PATTERNS.items():
            if keyword in text:
                hidden.append({
                    "keyword": keyword,
                    "implied_preference": meaning,
                })

        return hidden

    def _extract_salary_range(self, text: str) -> Dict[str, Optional[int]]:
        """提取薪资范围"""
        pattern = r"(\d+)\s*-?\s*(\d+)?\s*[万kK]?"

        matches = re.findall(pattern, text)

        if matches:
            # 取最后一个匹配（通常JD中薪资在后半部分）
            last_match = matches[-1]
            if last_match[1]:
                return {
                    "min": int(last_match[0]) * 10000,
                    "max": int(last_match[1]) * 10000,
                }
            else:
                return {"min": int(last_match[0]) * 10000, "max": None}

        return {"min": None, "max": None}

    def _extract_location(self, text: str) -> Optional[str]:
        """提取地点"""
        locations = ["北京", "上海", "深圳", "广州", "杭州", "南京", "苏州", "成都", "武汉", "西安"]

        for loc in locations:
            if loc in text:
                return loc

        return None
