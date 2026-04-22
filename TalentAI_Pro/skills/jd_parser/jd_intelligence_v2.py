"""
JD Intelligence Engine v2.0 - 智能JD分析引擎

功能升级：
1. 隐含偏好挖掘（JD没写但暗示的东西）
2. 公司超预期亮点注入
3. 候选人稀缺性评估
4. 薪资竞争力校准
5. 匹配难度评级
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class MatchingDifficulty(Enum):
    """匹配难度等级"""
    EASY = "容易"
    MEDIUM = "中等"
    HARD = "困难"
    VERY_HARD = "极难"


@dataclass
class JDSurpriseHighlight:
    """公司超预期亮点"""
    highlight: str
    source: str
    value_level: str  # 高/中/低


@dataclass
class SalaryCompetitiveness:
    """薪资竞争力分析"""
    jd_salary_min: int
    jd_salary_max: int
    market_salary_min: int
    market_salary_max: int
    competitiveness_score: float  # 0-100
    gap_percentage: float  # 正数表示低于市场，负数表示高于市场
    recommendation: str


@dataclass
class CandidateScarcity:
    """候选人稀缺性评估"""
    estimated_pool_size: str  # 如 "20-50人"
    scarcity_level: int  # 1-5星
    main_competition_sources: List[str]
    hiring_difficulty: str


@dataclass
class JDIntelligenceReport:
    """JD智能分析报告"""
    # 基础信息
    title: str
    location: str
    salary_range: Dict[str, Optional[int]]

    # 升级后的分析
    hidden_preferences: List[Dict[str, str]]
    surprise_highlights: List[JDSurpriseHighlight]
    scarcity: CandidateScarcity
    salary_competitiveness: SalaryCompetitiveness
    matching_difficulty: MatchingDifficulty
    difficulty_reasons: List[str]

    # JD吸引力评分
    attractiveness_score: float  # 0-100
    attractiveness_breakdown: Dict[str, float]

    # 猎头推岗策略
    headhunting_priority: str  # HIGH/MEDIUM/LOW
    targeting_direction: List[str]
    main_selling_points: List[str]
    risk_warnings: List[str]


class JDIntelligenceEngineV2:
    """
    JD智能分析引擎 v2.0

    输入：JD文本
    输出：完整的智能分析报告
    """

    # 稀缺性估算基准（按职位类型）
    SCARCITY_BASELINE = {
        "HR": {"easy": 500, "medium": 200, "hard": 50},
        "算法": {"easy": 300, "medium": 100, "hard": 30},
        "研发": {"easy": 800, "medium": 300, "hard": 100},
        "产品": {"easy": 400, "medium": 150, "hard": 50},
        "销售": {"easy": 1000, "medium": 500, "hard": 150},
        "高管": {"easy": 50, "medium": 20, "hard": 10},
    }

    # 市场薪资参考（年薪，单位：万）
    MARKET_SALARY_REFERENCE = {
        "P5": {"min": 30, "max": 50},
        "P6": {"min": 45, "max": 70},
        "P7": {"min": 60, "max": 100},
        "P8": {"min": 90, "max": 150},
        "P9": {"min": 130, "max": 250},
        "D": {"min": 150, "max": 400},
        "VP": {"min": 300, "max": 800},
    }

    # JD吸引力评分权重
    ATTRACTIVENESS_WEIGHTS = {
        "salary": 0.20,
        "company_highlights": 0.25,
        "growth_space": 0.20,
        "team_quality": 0.15,
        "equity": 0.10,
        "risk": 0.10,
    }

    def __init__(self):
        self.base_parser = None  # 可以注入基础parser

    def analyze(self, jd_text: str, job_type: str = "通用", market_data: Optional[Dict] = None) -> JDIntelligenceReport:
        """
        完整分析JD

        Args:
            jd_text: JD原文
            job_type: 职位类型（用于稀缺性估算）
            market_data: 市场数据（可选，用于薪资校准）

        Returns:
            JDIntelligenceReport: 完整的智能分析报告
        """
        # 1. 基础解析
        basic_info = self._parse_basic_info(jd_text)

        # 2. 隐含偏好挖掘
        hidden_prefs = self._extract_hidden_preferences(jd_text)

        # 3. 候选人稀缺性评估
        scarcity = self._assess_scarcity(jd_text, job_type, hidden_prefs)

        # 4. 薪资竞争力校准
        salary_competitiveness = self._calibrate_salary(
            basic_info.get("salary_range", {}),
            job_type,
            market_data
        )

        # 5. 匹配难度评级
        difficulty, difficulty_reasons = self._assess_difficulty(
            jd_text, hidden_prefs, scarcity, salary_competitiveness
        )

        # 6. JD吸引力评分
        attractiveness, breakdown = self._calculate_attractiveness(
            salary_competitiveness,
            difficulty,
            hidden_prefs
        )

        # 7. 猎头推岗策略
        priority, directions, selling_points, warnings = self._generate_strategy(
            hidden_prefs, scarcity, salary_competitiveness, difficulty
        )

        # 8. 超预期亮点（需要外部数据注入）
        surprise_highlights = []  # 等待Discovery Radar注入

        return JDIntelligenceReport(
            title=basic_info.get("title", "未知"),
            location=basic_info.get("location", "未知"),
            salary_range=basic_info.get("salary_range", {}),
            hidden_preferences=hidden_prefs,
            surprise_highlights=surprise_highlights,
            scarcity=scarcity,
            salary_competitiveness=salary_competitiveness,
            matching_difficulty=difficulty,
            difficulty_reasons=difficulty_reasons,
            attractiveness_score=attractiveness,
            attractiveness_breakdown=breakdown,
            headhunting_priority=priority,
            targeting_direction=directions,
            main_selling_points=selling_points,
            risk_warnings=warnings,
        )

    def _parse_basic_info(self, jd_text: str) -> Dict[str, Any]:
        """解析基础信息"""
        import re

        result = {
            "title": None,
            "location": None,
            "salary_range": {"min": None, "max": None},
        }

        # 提取职位名称
        title_match = re.search(r"招聘[：:]\s*([^\n]+)", jd_text)
        if title_match:
            result["title"] = title_match.group(1).strip()

        # 提取地点
        locations = ["北京", "上海", "深圳", "广州", "杭州", "南京", "苏州", "成都", "武汉", "西安"]
        for loc in locations:
            if loc in jd_text:
                result["location"] = loc
                break

        # 提取薪资
        salary_pattern = r"(\d+)\s*-?\s*(\d+)?\s*[万kK]?(?:/|年)?"
        salary_match = re.findall(salary_pattern, jd_text)
        if salary_match:
            last_match = salary_match[-1]
            if last_match[1]:
                result["salary_range"] = {
                    "min": int(last_match[0]) * 10000,
                    "max": int(last_match[1]) * 10000,
                }
            else:
                result["salary_range"] = {"min": int(last_match[0]) * 10000, "max": None}

        return result

    def _extract_hidden_preferences(self, jd_text: str) -> List[Dict[str, str]]:
        """
        挖掘隐含偏好 - v2.0增强版

        JD没写但暗示的东西
        """
        hidden_prefs = []

        patterns = {
            # 创业相关
            r"创业心态": {
                "meaning": "能接受低薪高股/高风险/一人多岗",
                "type": "价值观",
            },
            r"从0到1": {
                "meaning": "需要有创业公司/从0搭建经验，不能只在大公司做增量",
                "type": "经验",
            },
            r"创业公司": {
                "meaning": "能适应高不确定性/快速变化/资源有限环境",
                "type": "适应能力",
            },
            r"快速成长": {
                "meaning": "接受高强度工作/频繁出差/加班",
                "type": "工作强度",
            },

            # 技术相关
            r"AI.*人才|技术人才": {
                "meaning": "需要候选人和算法/技术候选人对话的能力，技术理解力是隐性必备项",
                "type": "技术理解",
            },
            r"算法|机器学习|深度学习": {
                "meaning": "需要候选人能理解技术细节，不是普通HR能胜任",
                "type": "技术深度",
            },

            # 组织相关
            r"组织搭建|组织发展": {
                "meaning": "不只是HR角色，还要参与公司战略，不只是执行层",
                "type": "战略参与",
            },
            r"团队管理|管理经验": {
                "meaning": "需要有带团队经验，不只是个人贡献者",
                "type": "管理能力",
            },
            r"跨团队|跨部门": {
                "meaning": "沟通能力强，能协调多方资源",
                "type": "沟通协调",
            },

            # 背景相关
            r"大厂经验": {
                "meaning": "流程规范，但可能缺乏创业经验，需要平衡",
                "type": "背景偏好",
            },
            r"海归|海外背景": {
                "meaning": "英语好，国际视野，但成本高",
                "type": "背景偏好",
            },
            r"985|211|清华|北大": {
                "meaning": "学历是筛选门槛，但非绝对",
                "type": "学历",
            },

            # 薪酬相关
            r"低薪|低现金": {
                "meaning": "公司无法提供大厂福利，需要用股权弥补",
                "type": "薪酬预期",
            },
            r"股权|期权": {
                "meaning": "核心卖点，弥补现金薪资差距",
                "type": "薪酬结构",
            },
        }

        for pattern, info in patterns.items():
            if pattern in jd_text:
                hidden_prefs.append({
                    "keyword": pattern,
                    "implied_preference": info["meaning"],
                    "type": info["type"],
                })

        return hidden_prefs

    def _assess_scarcity(
        self, jd_text: str, job_type: str, hidden_prefs: List[Dict[str, str]]
    ) -> CandidateScarcity:
        """
        评估候选人稀缺性

        估算满足条件的候选人池大小
        """
        baseline = self.SCARCITY_BASELINE.get(job_type, self.SCARCITY_BASELINE["通用"])

        # 根据隐含偏好调整
        difficulty_multiplier = 1.0
        competition_sources = []

        for pref in hidden_prefs:
            if pref["type"] == "经验" and "从0到1" in pref["keyword"]:
                difficulty_multiplier *= 0.3  # 从0搭建经验者更少
                competition_sources.append("有创业公司从0搭建经验的HR")
            if pref["type"] == "技术理解":
                difficulty_multiplier *= 0.2  # 技术理解力是稀缺能力
                competition_sources.append("有AI/技术背景的HR")
            if pref["type"] == "学历":
                difficulty_multiplier *= 0.5  # 985/211限制

        # 计算估算池
        estimated = int(baseline["hard"] * difficulty_multiplier)

        # 稀缺性评分
        if estimated <= 20:
            scarcity_level = 5
            pool_desc = "极稀缺（<20人）"
        elif estimated <= 50:
            scarcity_level = 4
            pool_desc = "很稀缺（20-50人）"
        elif estimated <= 100:
            scarcity_level = 3
            pool_desc = "较稀缺（50-100人）"
        elif estimated <= 300:
            scarcity_level = 2
            pool_desc = "一般（100-300人）"
        else:
            scarcity_level = 1
            pool_desc = "充足（>300人）"

        if not competition_sources:
            competition_sources = ["大厂HR", "创业公司HR", "猎头转型"]

        return CandidateScarcity(
            estimated_pool_size=pool_desc,
            scarcity_level=scarcity_level,
            main_competition_sources=competition_sources,
            hiring_difficulty=["容易", "中等", "困难", "很困难", "极困难"][scarcity_level - 1],
        )

    def _calibrate_salary(
        self,
        salary_range: Dict[str, Optional[int]],
        job_type: str,
        market_data: Optional[Dict] = None
    ) -> SalaryCompetitiveness:
        """
        校准薪资竞争力

        对比JD薪资 vs 市场薪资
        """
        jd_min = salary_range.get("min") or 0
        jd_max = salary_range.get("max") or jd_min

        # 估算职级
        level = self._estimate_level_from_salary(jd_min, jd_max)

        # 获取市场薪资
        market = self.MARKET_SALARY_REFERENCE.get(level, {"min": 50, "max": 100})
        if market_data:
            market = market_data.get(level, market)

        # 计算差距
        jd_avg = (jd_min + jd_max) / 2
        market_avg = (market["min"] + market["max"]) / 2
        gap_pct = ((jd_avg - market_avg) / market_avg) * 100

        # 竞争力评分
        if gap_pct >= 20:
            score = 90  # 高于市场
        elif gap_pct >= 10:
            score = 75
        elif gap_pct >= 0:
            score = 65
        elif gap_pct >= -20:
            score = 50  # 略低于市场
        elif gap_pct >= -40:
            score = 35  # 明显低于市场
        else:
            score = 20  # 严重低于市场

        # 建议
        if score >= 75:
            recommendation = "薪资有竞争力，可作为核心卖点"
        elif score >= 50:
            recommendation = "薪资略低于市场，需要用非现金收益弥补"
        else:
            recommendation = "薪资明显低于市场，必须用股权+赛道讲故事"

        return SalaryCompetitiveness(
            jd_salary_min=int(jd_min),
            jd_salary_max=int(jd_max),
            market_salary_min=market["min"] * 10000,
            market_salary_max=market["max"] * 10000,
            competitiveness_score=score,
            gap_percentage=round(gap_pct, 1),
            recommendation=recommendation,
        )

    def _estimate_level_from_salary(self, salary_min: int, salary_max: int) -> str:
        """根据薪资估算职级"""
        avg = (salary_min + salary_max) / 2
        avg_wan = avg / 10000

        if avg_wan >= 300:
            return "VP"
        elif avg_wan >= 150:
            return "D"
        elif avg_wan >= 90:
            return "P8"
        elif avg_wan >= 60:
            return "P7"
        elif avg_wan >= 45:
            return "P6"
        else:
            return "P5"

    def _assess_difficulty(
        self,
        jd_text: str,
        hidden_prefs: List[Dict[str, str]],
        scarcity: CandidateScarcity,
        salary: SalaryCompetitiveness
    ) -> tuple:
        """
        评估匹配难度

        Returns:
            (MatchingDifficulty, List[str]): 难度等级和原因
        """
        difficulty_score = 0
        reasons = []

        # 稀缺性影响
        if scarcity.scarcity_level >= 4:
            difficulty_score += 3
            reasons.append(f"候选人池极小（{scarcity.estimated_pool_size}）")
        elif scarcity.scarcity_level >= 3:
            difficulty_score += 2
            reasons.append("候选人池较小")

        # 薪资竞争力影响
        if salary.competitiveness_score < 50:
            difficulty_score += 3
            reasons.append(f"薪资低于市场{gap_pct:.0f}%，需候选人接受溢价换股权")
        elif salary.competitiveness_score < 65:
            difficulty_score += 1
            reasons.append("薪资略低于市场")

        # 隐含偏好复杂度
        if len(hidden_prefs) >= 4:
            difficulty_score += 2
            reasons.append("JD隐含偏好多，候选人需同时满足多项隐性条件")

        # 创业公司风险
        if any("创业" in pref["keyword"] for pref in hidden_prefs):
            difficulty_score += 1
            reasons.append("早期创业公司，风险较高")

        # 确定难度等级
        if difficulty_score >= 6:
            difficulty = MatchingDifficulty.VERY_HARD
        elif difficulty_score >= 4:
            difficulty = MatchingDifficulty.HARD
        elif difficulty_score >= 2:
            difficulty = MatchingDifficulty.MEDIUM
        else:
            difficulty = MatchingDifficulty.EASY

        return difficulty, reasons

    def _calculate_attractiveness(
        self,
        salary: SalaryCompetitiveness,
        difficulty: MatchingDifficulty,
        hidden_prefs: List[Dict[str, str]]
    ) -> tuple:
        """
        计算JD吸引力评分

        Returns:
            (总分, 分项评分)
        """
        breakdown = {}

        # 薪资贡献
        salary_score = salary.competitiveness_score
        breakdown["salary"] = salary_score

        # 公司亮点（暂定，待Discovery Radar补充）
        breakdown["company_highlights"] = 50  # 默认值

        # 成长空间
        growth_score = 70
        if any("组织搭建" in pref["keyword"] for pref in hidden_prefs):
            growth_score = 85  # 从0搭建是不可复制的经历
        breakdown["growth_space"] = growth_score

        # 团队质量（暂定）
        breakdown["team_quality"] = 50

        # 股权激励
        equity_score = 60
        if any("股权" in pref["keyword"] for pref in hidden_prefs):
            equity_score = 80
        breakdown["equity"] = equity_score

        # 风险系数
        risk_score = 70
        if difficulty in [MatchingDifficulty.HARD, MatchingDifficulty.VERY_HARD]:
            risk_score = 60
        breakdown["risk"] = risk_score

        # 总分
        total = sum(
            breakdown[key] * self.ATTRACTIVENESS_WEIGHTS[key]
            for key in self.ATTRACTIVENESS_WEIGHTS
        )

        return round(total, 1), breakdown

    def _generate_strategy(
        self,
        hidden_prefs: List[Dict[str, str]],
        scarcity: CandidateScarcity,
        salary: SalaryCompetitiveness,
        difficulty: MatchingDifficulty
    ) -> tuple:
        """
        生成猎头推岗策略

        Returns:
            (优先级, 寻猎方向, 主推卖点, 风险预警)
        """
        # 优先级
        if scarcity.scarcity_level >= 4 and salary.competitiveness_score >= 50:
            priority = "HIGH"
        elif scarcity.scarcity_level >= 3 or salary.competitiveness_score >= 50:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        # 寻猎方向
        directions = []
        if any("从0到1" in pref["keyword"] for pref in hidden_prefs):
            directions.append("具身智能/机器人公司HR一号位")
            directions.append("大厂硬件部门HR（想转型创业）")
        if any("技术" in pref["keyword"] for pref in hidden_prefs):
            directions.append("AI公司HR（已有具身智能认知）")

        # 主推卖点
        selling_points = []
        if salary.gap_percentage < -20:
            selling_points.append("股权期权（核心卖点，弥补薪资差距）")
        selling_points.append("技术自主权（直接参与技术人才决策）")
        if any("组织搭建" in pref["keyword"] for pref in hidden_prefs):
            selling_points.append("从0搭建（不可复制的经历积累）")
        selling_points.append("赛道红利（具身智能是下一个超级风口）")

        # 风险预警
        warnings = []
        if salary.gap_percentage < -40:
            warnings.append("候选人薪资预期若高于市场，需重新谈判")
        if scarcity.scarcity_level >= 4:
            warnings.append("寻猎周期可能较长，需做好候选人的预期管理")
        if difficulty in [MatchingDifficulty.HARD, MatchingDifficulty.VERY_HARD]:
            warnings.append("需要候选人有「愿意低薪换股权」的价值观")

        return priority, directions, selling_points, warnings

    def inject_surprise_highlights(self, report: JDIntelligenceReport, highlights: List[JDSurpriseHighlight]) -> JDIntelligenceReport:
        """
        注入超预期亮点（由Discovery Radar调用）

        更新报告中的公司超预期亮点
        """
        report.surprise_highlights = highlights

        # 重新计算吸引力评分
        total_highlight_value = sum(
            100 if h.value_level == "高" else 70 if h.value_level == "中" else 50
            for h in highlights
        )
        avg_highlight_score = min(total_highlight_value / max(len(highlights), 1), 100)
        report.attractiveness_breakdown["company_highlights"] = avg_highlight_score

        # 重新计算总分
        report.attractiveness_score = sum(
            report.attractiveness_breakdown[key] * self.ATTRACTIVENESS_WEIGHTS[key]
            for key in self.ATTRACTIVENESS_WEIGHTS
        )

        return report


def demo():
    """演示JD Intelligence Engine v2.0"""
    engine = JDIntelligenceEngineV2()

    jd_text = """
    招聘：具身智能HR负责人
    公司：某具身智能创业公司

    要求：
    - 985本科及以上学历
    - 10年以上HR经验
    - 有从0到1搭建招聘体系经验
    - 有AI/技术人才招聘经验优先
    - 有创业心态

    薪资：30-50万/年
    地点：北京
    """

    report = engine.analyze(jd_text, job_type="HR")

    print("=" * 60)
    print("JD Intelligence Engine v2.0 - 分析报告")
    print("=" * 60)

    print(f"\n【职位】{report.title}")
    print(f"【地点】{report.location}")
    print(f"【薪资】{report.salary_range.get('min', 0)/10000:.0f}-{report.salary_range.get('max', 0)/10000:.0f}万/年")

    print(f"\n【🔍 隐含偏好挖掘】（{len(report.hidden_preferences)}项）")
    for pref in report.hidden_preferences:
        print(f"  ✓ {pref['keyword']} → {pref['implied_preference']}")

    print(f"\n【📊 候选人稀缺性评估】")
    print(f"  稀缺度：{'⭐' * report.scarcity.scarcity_level}（{report.scarcity.estimated_pool_size}）")
    print(f"  招聘难度：{report.scarcity.hiring_difficulty}")
    print(f"  主要竞争来源：{', '.join(report.scarcity.main_competition_sources[:2])}")

    print(f"\n【💰 薪资竞争力】")
    print(f"  JD报价：{report.salary_competitiveness.jd_salary_min/10000:.0f}-{report.salary_competitiveness.jd_salary_max/10000:.0f}万")
    print(f"  市场参考：{report.salary_competitiveness.market_salary_min/10000:.0f}-{report.salary_competitiveness.market_salary_max/10000:.0f}万")
    print(f"  竞争力评分：{report.salary_competitiveness.competitiveness_score}/100")
    print(f"  建议：{report.salary_competitiveness.recommendation}")

    print(f"\n【🎯 匹配难度】{report.matching_difficulty.value}")
    for reason in report.difficulty_reasons:
        print(f"  - {reason}")

    print(f"\n【🏆 JD吸引力评分】{report.attractiveness_score}/100")
    for key, value in report.attractiveness_breakdown.items():
        print(f"  {key}: {value:.1f}")

    print(f"\n【🎯 猎头推岗策略】")
    print(f"  优先级：{report.headhunting_priority}")
    print(f"  寻猎方向：{', '.join(report.targeting_direction[:2])}")
    print(f"  主推卖点：{', '.join(report.main_selling_points[:2])}")
    if report.risk_warnings:
        print(f"  ⚠️ 风险预警：{report.risk_warnings[0]}")


if __name__ == "__main__":
    demo()