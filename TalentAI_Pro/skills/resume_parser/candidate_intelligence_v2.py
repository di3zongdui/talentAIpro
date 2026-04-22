"""
Candidate Intelligence Engine v2.0 - 智能候选人分析引擎

功能升级：
1. 全网背景交叉验证（GitHub/LinkedIn/脉脉）
2. 超预期亮点发现（开源/论文/创业）
3. 薪资/职级预测
4. 风险预警（频繁跳槽/职业断层）
5. 求职意向推测
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"


@dataclass
class SurpriseHighlight:
    """超预期亮点"""
    type: str  # github/paper/entrepreneurship/management/education
    highlight: str
    evidence: str
    value_level: str  # 高/中/低


@dataclass
class RiskWarning:
    """风险预警"""
    type: str  # job_hopping/career_gap/education_issue/salary_mismatch
    severity: RiskLevel
    description: str
    evidence: str


@dataclass
class SalaryPrediction:
    """薪资预测"""
    estimated_min: int  # 年薪，单位：分（方便计算）
    estimated_max: int
    estimated_level: str
    confidence: float  # 0-1
    basis: List[str]  # 预测依据


@dataclass
class JobIntentionInference:
    """求职意向推测"""
    preferred_direction: str  # 如 "具身智能/机器人"
    preferred_company_type: str  # 如 "创业公司"
    preferred_location: List[str]
    salary_expectation: str  # 如 "150-250万"
    reasoning: List[str]


@dataclass
class CandidateIntelligenceReport:
    """候选人智能分析报告"""
    # 基础信息
    name: str
    current_title: str
    current_company: str
    years_of_experience: int
    location: str

    # 升级后的分析
    surprise_highlights: List[SurpriseHighlight]
    risk_warnings: List[RiskWarning]
    salary_prediction: Optional[SalaryPrediction]
    job_intention: Optional[JobIntentionInference]
    estimated_level: str

    # 文化契合度
    culture_fit_score: float  # 0-100
    culture_fit_analysis: str

    # 综合评级
    overall_rating: str  # A/B/C/D
    rating_reasons: List[str]


class CandidateIntelligenceEngineV2:
    """
    候选人智能分析引擎 v2.0

    输入：简历文本 + 外部数据（可选）
    输出：完整的智能分析报告
    """

    # 超预期亮点识别模式
    SURPRISE_PATTERNS = {
        "github": [
            (r"GitHub|github|\.com/", "GitHub项目经历"),
            (r"star \d+|⭐ \d+", "GitHub项目有Star"),
            (r"open.?source|开源", "开源贡献"),
            (r"repository|repo", "代码仓库"),
            (r"contributor|commit", "代码贡献"),
        ],
        "paper": [
            (r"论文|paper|publication|顶会|SCI|CCF", "学术论文发表"),
            (r"专利|patent|发明专利", "专利持有"),
            (r"research|研究|实验室", "研究经历"),
        ],
        "entrepreneurship": [
            (r"创业|founder|联合创始人|CEO|CTO|CPO", "创业经历"),
            (r"融资|VC|投资|seed|pre.?A|A轮|B轮", "融资经历"),
            (r"产品上线|launch|release", "产品发布"),
        ],
        "management": [
            (r"团队|管理|team|下属|\d+人", "团队管理经验"),
            (r"汇报给|lead|director", "管理幅度"),
        ],
        "education": [
            (r"清华|北大|复旦|上交|浙大", "顶尖院校"),
            (r"博士|PhD|Doctor", "博士学历"),
            (r"硕士|研究生|Master", "硕士学历"),
            (r"海归|海外|留学", "海外背景"),
        ],
    }

    # 风险预警模式
    RISK_PATTERNS = {
        "job_hopping": [
            (r"\d+家公司|\d+段经历|频繁跳槽", "频繁换工作"),
            (r"每.*不到.*年|工作.*不足.*年", "平均任职时间短"),
        ],
        "career_gap": [
            (r"待业|失业|gap|空白期|未就业", "职业断层"),
            (r"\d{4}.*[-~].*未", "存在空白期"),
        ],
        "education_issue": [
            (r"学历存疑|造假|虚假", "学历存疑"),
            (r"非全|在职|函授|成人", "非全日制学历"),
        ],
    }

    # 薪资估算基准（年薪，单位：万）
    SALARY_REFERENCE = {
        "P5": {"min": 25, "max": 45, "base": 35},
        "P6": {"min": 40, "max": 65, "base": 50},
        "P7": {"min": 55, "max": 95, "base": 70},
        "P8": {"min": 80, "max": 140, "base": 100},
        "P9": {"min": 120, "max": 200, "base": 150},
        "D": {"min": 150, "max": 300, "base": 200},
        "VP": {"min": 250, "max": 600, "base": 400},
    }

    def __init__(self):
        pass

    def analyze(
        self,
        resume_text: str,
        external_data: Optional[Dict[str, Any]] = None
    ) -> CandidateIntelligenceReport:
        """
        完整分析候选人

        Args:
            resume_text: 简历原文
            external_data: 外部数据（可选）
                - github: GitHub数据
                - linkedin: LinkedIn数据
                - maimai: 脉脉数据

        Returns:
            CandidateIntelligenceReport: 完整的智能分析报告
        """
        # 1. 基础解析
        basic_info = self._parse_basic_info(resume_text)

        # 2. 超预期亮点发现
        surprise_highlights = self._discover_surprise_highlights(resume_text, external_data)

        # 3. 风险预警
        risk_warnings = self._detect_risk_warnings(resume_text, external_data)

        # 4. 职级估算
        estimated_level = self._estimate_level(
            basic_info.get("current_title", ""),
            basic_info.get("years_of_experience", 0),
            basic_info.get("education", {}),
            external_data
        )

        # 5. 薪资预测
        salary_prediction = self._predict_salary(
            estimated_level,
            basic_info.get("current_company", ""),
            external_data
        )

        # 6. 求职意向推测
        job_intention = self._infer_job_intention(
            resume_text, basic_info, external_data
        )

        # 7. 文化契合度
        culture_fit_score, culture_fit_analysis = self._assess_culture_fit(
            resume_text, basic_info, job_intention
        )

        # 8. 综合评级
        overall_rating, rating_reasons = self._calculate_overall_rating(
            surprise_highlights, risk_warnings, salary_prediction, culture_fit_score
        )

        return CandidateIntelligenceReport(
            name=basic_info.get("name", "未知"),
            current_title=basic_info.get("current_title", ""),
            current_company=basic_info.get("current_company", ""),
            years_of_experience=basic_info.get("years_of_experience", 0),
            location=basic_info.get("location", ""),
            surprise_highlights=surprise_highlights,
            risk_warnings=risk_warnings,
            salary_prediction=salary_prediction,
            job_intention=job_intention,
            estimated_level=estimated_level,
            culture_fit_score=culture_fit_score,
            culture_fit_analysis=culture_fit_analysis,
            overall_rating=overall_rating,
            rating_reasons=rating_reasons,
        )

    def _parse_basic_info(self, resume_text: str) -> Dict[str, Any]:
        """解析基础信息"""
        import re

        result = {
            "name": None,
            "current_title": None,
            "current_company": None,
            "years_of_experience": 0,
            "location": None,
            "education": {},
            "work_history": [],
        }

        # 提取姓名
        name_match = re.search(r"^【?([^】\n]+)】?", resume_text, re.MULTILINE)
        if name_match:
            result["name"] = name_match.group(1).strip()

        # 提取邮箱
        email_match = re.search(r"[\w.-]+@[\w.-]+\.\w+", resume_text)
        if email_match:
            result["email"] = email_match.group()

        # 提取电话
        phone_match = re.search(r"1[3-9]\d{9}", resume_text)
        if phone_match:
            result["phone"] = phone_match.group()

        # 提取地点
        locations = ["北京", "上海", "深圳", "广州", "杭州", "南京", "苏州", "成都", "武汉", "西安"]
        for loc in locations:
            if loc in resume_text:
                result["location"] = loc
                break

        # 提取当前职位和公司
        lines = resume_text.split("\n")
        for i, line in enumerate(lines):
            if any(kw in line for kw in ["职位", "岗位", "Title", "当前"]):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith("【"):
                        result["current_title"] = next_line
            if any(kw in line for kw in ["公司", "企业", "Company"]):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith("【"):
                        result["current_company"] = next_line

        # 提取工作年限
        year_patterns = [
            r"(\d+)\+?\s*年.*经验",
            r"经验\s*(\d+)\s*年",
            r"工作\s*(\d+)\s*年",
        ]
        for pattern in year_patterns:
            match = re.search(pattern, resume_text)
            if match:
                result["years_of_experience"] = int(match.group(1))
                break

        # 如果没找到，尝试从年份推算
        if not result["years_of_experience"]:
            year_mentions = re.findall(r"(20\d{2}|19\d{2})", resume_text)
            if len(year_mentions) >= 2:
                years = sorted([int(y) for y in set(year_mentions)])
                if len(years) >= 2:
                    result["years_of_experience"] = max(years) - min(years)

        # 提取教育背景
        education_levels = {"博士": "博士", "硕士": "硕士", "本科": "本科", "大专": "大专"}
        schools = ["清华", "北大", "复旦", "上交", "浙大", "中科大", "南大", "人大", "同济", "北航"]

        for level, desc in education_levels.items():
            if level in resume_text:
                result["education"]["degree"] = desc

        for school in schools:
            if school in resume_text:
                result["education"]["school"] = school
                break

        # 提取工作经历
        work_sections = re.findall(
            r"(20\d{2}[-~].*?(?=20\d{2}|教育|项目|$))",
            resume_text,
            re.DOTALL
        )
        result["work_history"] = [w.strip() for w in work_sections if w.strip()]

        return result

    def _discover_surprise_highlights(
        self, resume_text: str, external_data: Optional[Dict[str, Any]] = None
    ) -> List[SurpriseHighlight]:
        """
        发现超预期亮点

        从简历和外部数据中挖掘隐藏的亮点
        """
        highlights = []

        # 1. GitHub亮点
        github_data = external_data.get("github") if external_data else None
        if github_data:
            if github_data.get("star_count", 0) > 100:
                highlights.append(SurpriseHighlight(
                    type="github",
                    highlight=f"GitHub项目获{github_data.get('star_count')} Star",
                    evidence=f"https://github.com/{github_data.get('username')}",
                    value_level="高"
                ))
            if github_data.get("repo_count", 0) > 10:
                highlights.append(SurpriseHighlight(
                    type="github",
                    highlight=f"开源项目{github_data.get('repo_count')}个",
                    evidence="活跃开源贡献者",
                    value_level="中"
                ))
        else:
            # 从简历文本中检测GitHub相关
            if any(re.search(p, resume_text, re.IGNORECASE) for p, _ in self.SURPRISE_PATTERNS["github"]):
                highlights.append(SurpriseHighlight(
                    type="github",
                    highlight="GitHub开源项目经历",
                    evidence="简历中提及GitHub",
                    value_level="中"
                ))

        # 2. 学术论文亮点
        if any(re.search(p, resume_text, re.IGNORECASE) for p, _ in self.SURPRISE_PATTERNS["paper"]):
            if "顶会" in resume_text or "SCI" in resume_text:
                highlights.append(SurpriseHighlight(
                    type="paper",
                    highlight="顶会/SCI论文发表",
                    evidence="简历中提及顶会或SCI",
                    value_level="高"
                ))
            else:
                highlights.append(SurpriseHighlight(
                    type="paper",
                    highlight="学术研究经历",
                    evidence="简历中提及研究或论文",
                    value_level="中"
                ))

        # 3. 创业经历亮点
        if any(re.search(p, resume_text, re.IGNORECASE) for p, _ in self.SURPRISE_PATTERNS["entrepreneurship"]):
            if any(kw in resume_text for kw in ["A轮", "B轮", "融资", "VC"]):
                highlights.append(SurpriseHighlight(
                    type="entrepreneurship",
                    highlight="创业获融资经历",
                    evidence="简历中提及融资",
                    value_level="高"
                ))
            else:
                highlights.append(SurpriseHighlight(
                    type="entrepreneurship",
                    highlight="创业经历",
                    evidence="简历中提及创业",
                    value_level="中"
                ))

        # 4. 管理经验亮点
        management_match = re.search(r"管理.*?(\d+).*?人|团队.*?(\d+).*?人", resume_text)
        if management_match:
            team_size = int(management_match.group(1) or management_match.group(2))
            highlights.append(SurpriseHighlight(
                type="management",
                highlight=f"管理{team_size}人团队",
                evidence="简历中提及团队管理",
                value_level="高" if team_size >= 10 else "中"
            ))

        # 5. 学历亮点
        if "清华" in resume_text or "北大" in resume_text:
            highlights.append(SurpriseHighlight(
                type="education",
                highlight="顶尖院校背景",
                evidence="清华/北大",
                value_level="高"
            ))
        elif "博士" in resume_text:
            highlights.append(SurpriseHighlight(
                type="education",
                highlight="博士学历",
                evidence="博士学位",
                value_level="高"
            ))
        elif "硕士" in resume_text:
            highlights.append(SurpriseHighlight(
                type="education",
                highlight="硕士学历",
                evidence="硕士学位",
                value_level="中"
            ))

        # 6. 大厂背景亮点
        top_companies = ["字节", "阿里", "腾讯", "百度", "美团", "京东", "华为", "大疆", "小米"]
        for company in top_companies:
            if company in resume_text:
                highlights.append(SurpriseHighlight(
                    type="background",
                    highlight=f"{company}系背景",
                    evidence=f"曾在{company}工作",
                    value_level="高" if company in ["大疆", "字节", "华为"] else "中"
                ))
                break

        return highlights

    def _detect_risk_warnings(
        self, resume_text: str, external_data: Optional[Dict[str, Any]] = None
    ) -> List[RiskWarning]:
        """
        检测风险预警

        识别潜在风险点
        """
        warnings = []

        # 1. 频繁跳槽
        job_changes = re.findall(r"(20\d{2})[-~](20\d{2})", resume_text)
        if len(job_changes) >= 4:
            # 检查平均任职时间
            total_years = 0
            for start, end in job_changes:
                total_years += int(end) - int(start)
            avg_years = total_years / len(job_changes) if job_changes else 0
            if avg_years < 2:
                warnings.append(RiskWarning(
                    type="job_hopping",
                    severity=RiskLevel.HIGH,
                    description=f"平均任职时间约{avg_years:.1f}年，较为频繁",
                    evidence=f"简历中出现{len(job_changes)}段工作经历"
                ))

        # 2. 职业断层
        if any(re.search(p, resume_text, re.IGNORECASE) for p, _ in self.RISK_PATTERNS["career_gap"]):
            warnings.append(RiskWarning(
                type="career_gap",
                severity=RiskLevel.MEDIUM,
                description="存在职业断层或空白期",
                evidence="简历中提及待业或空白期"
            ))

        # 3. 学历问题
        if "非全" in resume_text or "函授" in resume_text:
            warnings.append(RiskWarning(
                type="education_issue",
                severity=RiskLevel.MEDIUM,
                description="学历为非全日制",
                evidence="简历中提及非全日制"
            ))

        return warnings

    def _estimate_level(
        self,
        title: str,
        years: int,
        education: Dict,
        external_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        估算职级

        综合职位名称、工作年限、学历、外部数据
        """
        title_lower = title.lower() if title else ""

        # 职位名称判断
        if any(kw in title_lower for kw in ["总监", "Director", "VP", "Vice President", "总经理", "CEO"]):
            if years >= 12:
                return "VP"
            return "D"
        elif any(kw in title_lower for kw in ["高级总监", "Senior Director"]):
            return "D+"
        elif any(kw in title_lower for kw in ["经理", "Manager", "Senior Manager"]):
            if years >= 8:
                return "M+"
            return "M"
        elif any(kw in title_lower for kw in ["主管", "Lead", "专家", "Expert", "Staff"]):
            return "S"
        elif any(kw in title_lower for kw in ["高级", "Senior"]):
            return "P6"
        elif any(kw in title_lower for kw in ["初级", "Junior", "助理", "Intern"]):
            return "P5"

        # 根据年限推算
        if years >= 15:
            return "D+"
        elif years >= 12:
            return "D"
        elif years >= 10:
            return "M+"
        elif years >= 7:
            return "M"
        elif years >= 5:
            return "S"
        elif years >= 3:
            return "P6"
        else:
            return "P5"

    def _predict_salary(
        self,
        level: str,
        current_company: str,
        external_data: Optional[Dict[str, Any]] = None
    ) -> SalaryPrediction:
        """
        预测薪资

        基于职级、公司背景、外部数据
        """
        reference = self.SALARY_REFERENCE.get(level, {"min": 30, "max": 60, "base": 45})

        # 调整系数
        multiplier = 1.0
        basis = [f"基于{level}职级"]

        # 公司加成
        top_companies = ["字节", "阿里", "腾讯", "百度", "美团", "大疆", "华为"]
        if any(c in current_company for c in top_companies):
            multiplier *= 1.2
            basis.append(f"大厂背景加成20%")

        # 外部数据加成
        if external_data:
            if external_data.get("github_star_count", 0) > 500:
                multiplier *= 1.15
                basis.append("GitHub高Star加成15%")

        # 计算范围
        estimated_min = int(reference["min"] * multiplier)
        estimated_max = int(reference["max"] * multiplier)

        return SalaryPrediction(
            estimated_min=estimated_min * 10000,  # 转换为分
            estimated_max=estimated_max * 10000,
            estimated_level=level,
            confidence=0.75,
            basis=basis
        )

    def _infer_job_intention(
        self,
        resume_text: str,
        basic_info: Dict,
        external_data: Optional[Dict[str, Any]] = None
    ) -> Optional[JobIntentionInference]:
        """
        推测求职意向

        从简历和外部数据中推断
        """
        reasoning = []

        # 推测方向
        preferred_direction = "待定"
        direction_keywords = {
            "具身智能": ["具身", "机器人", "robot"],
            "AI/ML": ["人工智能", "机器学习", "AI", "算法"],
            "互联网": ["互联网", "电商", "平台"],
            "硬件": ["硬件", "芯片", "嵌入式", "大疆"],
        }

        for direction, keywords in direction_keywords.items():
            if any(kw in resume_text.lower() for kw in keywords):
                preferred_direction = direction
                reasoning.append(f"简历中多次提及{direction}相关内容")
                break

        # 推测公司类型
        preferred_company_type = "不限"
        if "创业" in resume_text or "创业" in str(external_data or {}):
            preferred_company_type = "创业公司"
            reasoning.append("有创业经历，更倾向创业环境")
        elif "大厂" in resume_text:
            preferred_company_type = "大厂"
            reasoning.append("大厂背景，可能希望稳定")

        # 推测地点
        preferred_location = [basic_info.get("location", "北京")]
        if not preferred_location[0]:
            preferred_location = ["北京"]

        # 推测薪资预期
        salary_expectation = "待确认"
        salary_match = re.search(r"期望.*?(\d+)-(\d+)", resume_text)
        if salary_match:
            salary_expectation = f"{salary_match.group(1)}-{salary_match.group(2)}万"

        return JobIntentionInference(
            preferred_direction=preferred_direction,
            preferred_company_type=preferred_company_type,
            preferred_location=preferred_location,
            salary_expectation=salary_expectation,
            reasoning=reasoning
        )

    def _assess_culture_fit(
        self,
        resume_text: str,
        basic_info: Dict,
        job_intention: Optional[JobIntentionInference]
    ) -> tuple:
        """
        评估文化契合度

        Returns:
            (score, analysis)
        """
        score = 70.0
        analysis_parts = []

        # 稳定性加成
        years = basic_info.get("years_of_experience", 0)
        if years >= 5:
            score += 10
            analysis_parts.append("工作年限充足，稳定性较好")

        # 创业匹配
        if job_intention and job_intention.preferred_company_type == "创业公司":
            score += 10
            analysis_parts.append("倾向创业环境，与创业公司文化契合")

        # 教育背景
        education = basic_info.get("education", {})
        if education.get("school") in ["清华", "北大"]:
            score += 5
            analysis_parts.append("顶尖院校背景")

        return min(score, 100), "；".join(analysis_parts) if analysis_parts else "文化契合度一般"

    def _calculate_overall_rating(
        self,
        highlights: List[SurpriseHighlight],
        warnings: List[RiskWarning],
        salary_pred: Optional[SalaryPrediction],
        culture_fit: float
    ) -> tuple:
        """
        计算综合评级

        Returns:
            (rating, reasons)
        """
        score = 70.0
        reasons = []

        # 亮点加分
        high_value_count = sum(1 for h in highlights if h.value_level == "高")
        if high_value_count >= 2:
            score += 15
            reasons.append(f"拥有{high_value_count}项高价值超预期亮点")
        elif high_value_count == 1:
            score += 8
            reasons.append("有1项高价值亮点")

        # 风险扣分
        high_risk_count = sum(1 for w in warnings if w.severity == RiskLevel.HIGH)
        if high_risk_count > 0:
            score -= high_risk_count * 15
            reasons.append(f"存在{high_risk_count}项高风险")

        # 文化契合度
        if culture_fit >= 80:
            score += 5
        elif culture_fit < 60:
            score -= 10

        # 定级
        score = max(0, min(100, score))
        if score >= 85:
            rating = "A"
        elif score >= 70:
            rating = "B"
        elif score >= 55:
            rating = "C"
        else:
            rating = "D"

        return rating, reasons


def demo():
    """演示Candidate Intelligence Engine v2.0"""
    engine = CandidateIntelligenceEngineV2()

    resume_text = """
    【Levi Li】

    邮箱：levi.li@example.com
    电话：13900001111
    地点：北京

    当前职位：HR总监
    当前公司：某具身智能创业公司（创业中）

    工作经历：
    2024-至今：具身智能创业，HR负责人
    2020-2024：某大厂，HR总监（P9级），管理50人团队
    2015-2020：某互联网公司，HR经理
    2012-2015：某咨询公司，HR专员

    教育背景：
    硕士 - 清华大学
    本科 - 985高校

    技能：
    人力资源管理、招聘体系搭建、组织发展、绩效管理
    """

    report = engine.analyze(resume_text)

    print("=" * 60)
    print("Candidate Intelligence Engine v2.0 - 分析报告")
    print("=" * 60)

    print(f"\n【候选人】{report.name}")
    print(f"【当前职位】{report.current_title} @ {report.current_company}")
    print(f"【工作年限】{report.years_of_experience}年")
    print(f"【估算职级】{report.estimated_level}")

    print(f"\n【✨ 超预期亮点】（{len(report.surprise_highlights)}项）")
    for h in report.surprise_highlights:
        print(f"  ✓ [{h.type}] {h.highlight}")
        print(f"    证据：{h.evidence}")
        print(f"    价值：{h.value_level}")

    print(f"\n【⚠️ 风险预警】（{len(report.risk_warnings)}项）")
    if report.risk_warnings:
        for w in report.risk_warnings:
            print(f"  ⚠️ [{w.severity.value}] {w.description}")
            print(f"    证据：{w.evidence}")
    else:
        print("  ✓ 无明显风险")

    print(f"\n【💰 薪资预测】")
    if report.salary_prediction:
        print(f"  估算范围：{report.salary_prediction.estimated_min/10000:.0f}-{report.salary_prediction.estimated_max/10000:.0f}万/年")
        print(f"  对标职级：{report.salary_prediction.estimated_level}")
        print(f"  置信度：{report.salary_prediction.confidence*100:.0f}%")
        print(f"  依据：{'；'.join(report.salary_prediction.basis)}")

    print(f"\n【🎯 求职意向推测】")
    if report.job_intention:
        print(f"  方向：{report.job_intention.preferred_direction}")
        print(f"  公司类型：{report.job_intention.preferred_company_type}")
        print(f"  期望薪资：{report.job_intention.salary_expectation}")
        if report.job_intention.reasoning:
            print(f"  推断依据：{'；'.join(report.job_intention.reasoning[:2])}")

    print(f"\n【🎨 文化契合度】{report.culture_fit_score}/100")
    print(f"  {report.culture_fit_analysis}")

    print(f"\n【🏆 综合评级】{report.overall_rating}")
    for reason in report.rating_reasons:
        print(f"  - {reason}")


if __name__ == "__main__":
    demo()