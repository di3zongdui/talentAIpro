"""
Resume Parser - 简历解析器

功能：
1. 简历文本 → 结构化字段
2. 经验年限提取
3. 技能提取
4. 薪资估算（待实现）
5. 风险预警（待实现）
"""
from typing import Dict, List, Any, Optional
import re


class ResumeParser:
    """简历解析器"""

    # 常见技能关键词
    SKILL_KEYWORDS = [
        "Python", "Java", "Go", "Rust", "C++", "JavaScript", "TypeScript",
        "React", "Vue", "Angular", "Node.js", "Django", "FastAPI", "Spring",
        "AWS", "Azure", "GCP", "Kubernetes", "Docker", "Linux",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis",
        "Agile", "Scrum", "DevOps", "CI/CD",
        "Leadership", "Management", "Strategy",
        "Product", "Design", "UX", "UI",
        "Sales", "Marketing", "Operations",
    ]

    def __init__(self):
        self.raw_text = ""
        self.parsed_data = {}

    def parse(self, resume_text: str) -> Dict[str, Any]:
        """
        解析简历文本

        Args:
            resume_text: 简历原文

        Returns:
            解析后的结构化数据
        """
        self.raw_text = resume_text

        # 1. 提取基本信息
        basic_info = self._extract_basic_info(resume_text)

        # 2. 提取技能
        skills = self._extract_skills(resume_text)

        # 3. 估算工作年限
        years_of_experience = self._extract_experience_years(resume_text)

        # 4. 提取教育背景
        education = self._extract_education(resume_text)

        # 5. 估算职级
        estimated_level = self._estimate_level(
            basic_info.get("current_title", ""), years_of_experience
        )

        # 6. 构建结果
        result = {
            "raw_text": resume_text,
            "name": basic_info.get("name"),
            "email": basic_info.get("email"),
            "phone": basic_info.get("phone"),
            "location": basic_info.get("location"),
            "current_title": basic_info.get("current_title"),
            "current_company": basic_info.get("current_company"),
            "skills": skills,
            "years_of_experience": years_of_experience,
            "education": education,
            "estimated_level": estimated_level,
        }

        self.parsed_data = result
        return result

    def _extract_basic_info(self, text: str) -> Dict[str, Optional[str]]:
        """提取基本信息"""
        info = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "current_title": None,
            "current_company": None,
        }

        # 提取邮箱
        email_match = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
        if email_match:
            info["email"] = email_match.group()

        # 提取电话
        phone_match = re.search(r"1[3-9]\d{9}", text)
        if phone_match:
            info["phone"] = phone_match.group()

        # 提取姓名
        name_match = re.search(r"^【?([^】\n]+)】?", text, re.MULTILINE)
        if name_match:
            info["name"] = name_match.group(1).strip()

        # 提取地点
        locations = ["北京", "上海", "深圳", "广州", "杭州", "南京", "苏州", "成都", "武汉", "西安"]
        for loc in locations:
            if loc in text:
                info["location"] = loc
                break

        # 提取当前职位和公司
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(kw in line for kw in ["职位", "岗位", "Title"]):
                if i + 1 < len(lines):
                    info["current_title"] = lines[i + 1].strip()
            if any(kw in line for kw in ["公司", "企业", "Company"]):
                if i + 1 < len(lines):
                    info["current_company"] = lines[i + 1].strip()

        return info

    def _extract_skills(self, text: str) -> List[str]:
        """提取技能"""
        found_skills = []
        text_lower = text.lower()

        for skill in self.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return list(set(found_skills))

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """估算工作年限"""
        patterns = [
            r"(\d+)\+?\s*年",
            r"(\d+)\s*年经验",
            r"工作\s*(\d+)\s*年",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        year_mentions = re.findall(r"20\d{2}", text)
        if len(year_mentions) >= 2:
            years = [int(y) for y in year_mentions]
            return max(years) - min(years)

        return None

    def _extract_education(self, text: str) -> Optional[Dict[str, str]]:
        """提取教育背景"""
        education_levels = {
            "博士": "博士",
            "硕士": "硕士",
            "研究生": "硕士",
            "本科": "本科",
            "学士": "本科",
            "大专": "大专",
        }

        schools = ["清华", "北大", "复旦", "上交", "浙大", "中科大", "南大", "人大", "同济", "北航"]

        result = {}

        for level, desc in education_levels.items():
            if level in text:
                result["degree"] = desc

        for school in schools:
            if school in text:
                result["school"] = school
                break

        return result if result else None

    def _estimate_level(self, title: str, years: Optional[int]) -> str:
        """估算职级"""
        if not title and not years:
            return "Unknown"

        title_lower = title.lower() if title else ""

        if any(kw in title_lower for kw in ["总监", "Director", "VP", "Vice President"]):
            return "D"
        elif any(kw in title_lower for kw in ["经理", "Manager", "Senior"]):
            return "M"
        elif any(kw in title_lower for kw in ["主管", "Lead"]):
            return "S"
        elif any(kw in title_lower for kw in ["专家", "Expert", "Staff"]):
            return "P7-P8"
        elif any(kw in title_lower for kw in ["高级", "Senior"]):
            return "P6"
        elif any(kw in title_lower for kw in ["初级", "Junior", "助理", "Intern"]):
            return "P5以下"

        if years:
            if years >= 15:
                return "D+"
            elif years >= 10:
                return "D"
            elif years >= 7:
                return "M"
            elif years >= 5:
                return "M/S"
            elif years >= 3:
                return "S"
            else:
                return "P5-P6"

        return "P5-P6"