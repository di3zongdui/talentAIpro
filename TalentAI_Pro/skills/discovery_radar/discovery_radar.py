"""
Discovery Radar - 双向背景尽调雷达

功能：
- 候选人侧：LinkedIn/GitHub/脉脉/论文专利
- 公司侧：融资信息/团队背景/舆情分析

数据源优先级：
1. web_search (miaoda) - 中文内容覆盖最好
2. Tavily API - 英文内容覆盖较好
3. GitHub API - 技术岗专项
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class IntelligenceSource:
    """情报来源"""
    source_name: str  # 如 "GitHub", "LinkedIn"
    url: Optional[str]
    data: Dict[str, Any]
    reliability: str  # 高/中/低
    last_updated: str


@dataclass
class CandidateRadarReport:
    """候选人雷达报告"""
    name: str
    linkedin_insights: Optional[IntelligenceSource]
    github_insights: Optional[IntelligenceSource]
    maimai_insights: Optional[IntelligenceSource]
    paper_patent_insights: Optional[IntelligenceSource]

    # 综合亮点
    overall_surprise_highlights: List[Dict[str, str]]
    competitive_analysis: str  # 市场竞争分析
    hiring_recommendation: str  # 招聘建议


@dataclass
class CompanyRadarReport:
    """公司雷达报告"""
    company_name: str
    funding_info: Optional[IntelligenceSource]
    team_background: Optional[IntelligenceSource]
    public_sentiment: Optional[IntelligenceSource]
    competitor_comparison: Optional[IntelligenceSource]

    # 综合亮点
    overall_surprise_highlights: List[Dict[str, str]]
    risk_alerts: List[str]
    investment_recommendation: str  # 投资/合作建议


class DiscoveryRadar:
    """
    Discovery Radar - 双向背景尽调雷达

    用于招聘者和求职者两侧的背景调查
    """

    def __init__(self, search_func=None, github_api=None):
        """
        初始化雷达

        Args:
            search_func: 搜索函数（web_search或Tavily）
            github_api: GitHub API客户端
        """
        self.search_func = search_func
        self.github_api = github_api

    def investigate_candidate(
        self,
        name: str,
        company: Optional[str] = None,
        title: Optional[str] = None,
        github_username: Optional[str] = None
    ) -> CandidateRadarReport:
        """
        调查候选人背景

        Args:
            name: 候选人姓名
            company: 当前公司
            title: 当前职位
            github_username: GitHub用户名

        Returns:
            CandidateRadarReport: 候选人雷达报告
        """
        insights = {}

        # 1. LinkedIn调查
        insights["linkedin"] = self._search_linkedin(name, company, title)

        # 2. GitHub调查
        insights["github"] = self._search_github(name, github_username)

        # 3. 脉脉调查
        insights["maimai"] = self._search_maimai(name, company)

        # 4. 论文/专利调查
        insights["paper_patent"] = self._search_paper_patent(name)

        # 整合亮点
        overall_highlights = self._aggregate_candidate_highlights(insights)

        # 市场竞争分析
        competitive_analysis = self._analyze_candidate_competition(insights)

        # 招聘建议
        hiring_recommendation = self._generate_hiring_recommendation(insights, overall_highlights)

        return CandidateRadarReport(
            name=name,
            linkedin_insights=insights.get("linkedin"),
            github_insights=insights.get("github"),
            maimai_insights=insights.get("maimai"),
            paper_patent_insights=insights.get("paper_patent"),
            overall_surprise_highlights=overall_highlights,
            competitive_analysis=competitive_analysis,
            hiring_recommendation=hiring_recommendation,
        )

    def investigate_company(
        self,
        company_name: str,
        industry: Optional[str] = None
    ) -> CompanyRadarReport:
        """
        调查公司背景

        Args:
            company_name: 公司名称
            industry: 行业

        Returns:
            CompanyRadarReport: 公司雷达报告
        """
        insights = {}

        # 1. 融资信息
        insights["funding"] = self._search_funding(company_name)

        # 2. 团队背景
        insights["team"] = self._search_team_background(company_name)

        # 3. 舆情分析
        insights["sentiment"] = self._search_public_sentiment(company_name)

        # 4. 竞品对比
        insights["competitor"] = self._search_competitor(company_name, industry)

        # 整合亮点
        overall_highlights = self._aggregate_company_highlights(insights)

        # 风险预警
        risk_alerts = self._detect_company_risks(insights)

        # 投资/合作建议
        recommendation = self._generate_company_recommendation(insights, risk_alerts)

        return CompanyRadarReport(
            company_name=company_name,
            funding_info=insights.get("funding"),
            team_background=insights.get("team"),
            public_sentiment=insights.get("sentiment"),
            competitor_comparison=insights.get("competitor"),
            overall_surprise_highlights=overall_highlights,
            risk_alerts=risk_alerts,
            investment_recommendation=recommendation,
        )

    def _search_linkedin(
        self, name: str, company: Optional[str], title: Optional[str]
    ) -> Optional[IntelligenceSource]:
        """搜索LinkedIn"""
        if not self.search_func:
            return None

        query = f"{name} LinkedIn {company or ''} {title or ''}".strip()
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="LinkedIn",
                url=results[0].get("url"),
                data={"snippet": results[0].get("snippet", ""), "positions": []},
                reliability="中",
                last_updated="最近"
            )
        return None

    def _search_github(
        self, name: str, github_username: Optional[str] = None
    ) -> Optional[IntelligenceSource]:
        """搜索GitHub"""
        if github_username and self.github_api:
            # 直接API调用
            data = self.github_api.get_user(github_username)
            if data:
                return IntelligenceSource(
                    source_name="GitHub",
                    url=f"https://github.com/{github_username}",
                    data=data,
                    reliability="高",
                    last_updated="实时"
                )

        if self.search_func:
            query = f"{name} GitHub site:github.com"
            results = self.search_func(query)
            if results:
                return IntelligenceSource(
                    source_name="GitHub",
                    url=results[0].get("url"),
                    data={"snippet": results[0].get("snippet", "")},
                    reliability="中",
                    last_updated="最近"
                )

        return None

    def _search_maimai(
        self, name: str, company: Optional[str] = None
    ) -> Optional[IntelligenceSource]:
        """搜索脉脉"""
        if not self.search_func:
            return None

        query = f"{name} 脉脉 {company or ''}".strip()
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="脉脉",
                url=None,
                data={"sentiment": results[0].get("snippet", "")},
                reliability="中",
                last_updated="最近"
            )
        return None

    def _search_paper_patent(
        self, name: str
    ) -> Optional[IntelligenceSource]:
        """搜索论文/专利"""
        if not self.search_func:
            return None

        query = f"{name} 论文 专利 Google Scholar"
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="论文/专利",
                url=None,
                data={"publications": [r.get("snippet", "") for r in results[:3]]},
                reliability="高",
                last_updated="最近"
            )
        return None

    def _search_funding(self, company_name: str) -> Optional[IntelligenceSource]:
        """搜索融资信息"""
        if not self.search_func:
            return None

        query = f"{company_name} 融资 投资 轮次 估值 {datetime.now().year}"
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="融资信息",
                url=None,
                data={"funding_details": [r.get("snippet", "") for r in results[:3]]},
                reliability="高",
                last_updated="最近"
            )
        return None

    def _search_team_background(self, company_name: str) -> Optional[IntelligenceSource]:
        """搜索团队背景"""
        if not self.search_func:
            return None

        query = f"{company_name} 团队 CTO CEO 创始人 背景 LinkedIn"
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="团队背景",
                url=None,
                data={"team_info": [r.get("snippet", "") for r in results[:3]]},
                reliability="中",
                last_updated="最近"
            )
        return None

    def _search_public_sentiment(self, company_name: str) -> Optional[IntelligenceSource]:
        """搜索舆情"""
        if not self.search_func:
            return None

        query = f"{company_name} 脉脉 看准 员工评价 离职 加班"
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="舆情分析",
                url=None,
                data={"sentiment": [r.get("snippet", "") for r in results[:3]]},
                reliability="中",
                last_updated="最近"
            )
        return None

    def _search_competitor(
        self, company_name: str, industry: Optional[str] = None
    ) -> Optional[IntelligenceSource]:
        """搜索竞品对比"""
        if not self.search_func:
            return None

        industry_query = industry or ""
        query = f"{company_name} 竞品 对比 市场份额 {industry_query}"
        results = self.search_func(query)

        if results:
            return IntelligenceSource(
                source_name="竞品对比",
                url=None,
                data={"competitors": [r.get("snippet", "") for r in results[:3]]},
                reliability="中",
                last_updated="最近"
            )
        return None

    def _aggregate_candidate_highlights(
        self, insights: Dict
    ) -> List[Dict[str, str]]:
        """整合候选人亮点"""
        highlights = []

        # GitHub亮点
        if insights.get("github"):
            data = insights["github"].data
            if isinstance(data, dict):
                if data.get("star_count", 0) > 100:
                    highlights.append({
                        "type": "github",
                        "highlight": f"GitHub项目获{data.get('star_count')} Star",
                        "source": "GitHub"
                    })
                if data.get("followers", 0) > 500:
                    highlights.append({
                        "type": "network",
                        "highlight": f"GitHub {data.get('followers')} 关注者",
                        "source": "GitHub"
                    })

        # 论文亮点
        if insights.get("paper_patent"):
            highlights.append({
                "type": "academic",
                "highlight": "有学术论文发表",
                "source": "论文数据库"
            })

        return highlights[:5]  # 最多5条

    def _aggregate_company_highlights(
        self, insights: Dict
    ) -> List[Dict[str, str]]:
        """整合公司亮点"""
        highlights = []

        # 融资亮点
        if insights.get("funding"):
            data = insights["funding"].data
            if isinstance(data, dict):
                funding_details = data.get("funding_details", [])
                if funding_details:
                    highlights.append({
                        "type": "funding",
                        "highlight": f"最近融资：{funding_details[0][:50]}",
                        "source": "融资数据库"
                    })

        # 团队亮点
        if insights.get("team"):
            highlights.append({
                "type": "team",
                "highlight": "创始团队背景优秀",
                "source": "公开信息"
            })

        return highlights[:5]  # 最多5条

    def _analyze_candidate_competition(self, insights: Dict) -> str:
        """分析候选人市场竞争"""
        # 基于已有信息生成分析
        analysis = "根据公开数据分析："

        if insights.get("github"):
            analysis += "\n- 技术实力：GitHub活跃度高，技术能力有据可查"

        if insights.get("paper_patent"):
            analysis += "\n- 学术深度：有学术背景，竞争壁垒较高"

        if insights.get("maimai"):
            analysis += "\n- 行业口碑：脉脉有相关信息，可进一步核实"

        return analysis if analysis != "根据公开数据分析：" else "数据有限，建议进一步调查"

    def _generate_hiring_recommendation(
        self, insights: Dict, highlights: List[Dict]
    ) -> str:
        """生成招聘建议"""
        if len(highlights) >= 3:
            return "候选人亮点突出，建议优先联系"
        elif len(highlights) >= 1:
            return "候选人有亮点，可以进一步接触"
        else:
            return "候选人背景数据有限，建议传统面试评估"

    def _detect_company_risks(self, insights: Dict) -> List[str]:
        """检测公司风险"""
        risks = []

        # 舆情风险
        if insights.get("sentiment"):
            sentiment_data = insights["sentiment"].data.get("sentiment", [])
            negative_count = sum(1 for s in sentiment_data if "差评" in s or "加班" in s)
            if negative_count >= 2:
                risks.append("员工评价负面较多，需关注企业文化")

        return risks

    def _generate_company_recommendation(
        self, insights: Dict, risks: List[str]
    ) -> str:
        """生成公司建议"""
        if insights.get("funding") and not risks:
            return "公司融资顺利，舆情正面，建议积极推进招聘"
        elif risks:
            return f"公司存在风险：{risks[0]}，建议谨慎评估"
        else:
            return "公司信息有限，建议进一步尽职调查"


from datetime import datetime


def demo():
    """演示Discovery Radar"""
    radar = DiscoveryRadar(search_func=lambda q: [{"snippet": f"测试数据: {q}", "url": None}])

    print("=" * 60)
    print("Discovery Radar - 演示")
    print("=" * 60)

    # 候选人调查演示
    print("\n【候选人背景调查】")
    report = radar.investigate_candidate(
        name="Levi Li",
        company="某具身智能公司",
        title="HR总监"
    )
    print(f"候选人：{report.name}")
    print(f"超预期亮点：{len(report.overall_surprise_highlights)}项")
    for h in report.overall_surprise_highlights:
        print(f"  - [{h['type']}] {h['highlight']}")
    print(f"招聘建议：{report.hiring_recommendation}")

    # 公司调查演示
    print("\n【公司背景调查】")
    company_report = radar.investigate_company(
        company_name="自变量机器人",
        industry="具身智能"
    )
    print(f"公司：{company_report.company_name}")
    print(f"超预期亮点：{len(company_report.overall_surprise_highlights)}项")
    for h in company_report.overall_surprise_highlights:
        print(f"  - [{h['type']}] {h['highlight']}")
    if company_report.risk_alerts:
        print(f"风险预警：{company_report.risk_alerts[0]}")


if __name__ == "__main__":
    demo()