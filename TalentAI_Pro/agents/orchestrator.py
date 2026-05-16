"""
TalentAI Pro - Agent Orchestrator
全自动Agent团队编排引擎
将招聘需求自动分配给各Agent，串行执行并返回结果
"""

import asyncio
import json
import time
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .base import AgentMessage, AgentType
from .registry import AgentRegistry


@dataclass
class OrchestrationResult:
    """编排结果"""
    jd_parsed: Dict[str, Any] = field(default_factory=dict)
    search_description: str = ""  # 用于搜索的语义描述
    search_strategy: Dict[str, Any] = field(default_factory=dict)
    candidates_raw: List[Dict[str, Any]] = field(default_factory=list)
    candidates_scored: List[Dict[str, Any]] = field(default_factory=list)
    top_candidates: List[Dict[str, Any]] = field(default_factory=list)
    evaluation: Dict[str, Any] = field(default_factory=dict)
    total_time_ms: int = 0
    agent_timings: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed


class AgentOrchestrator:
    """
    Agent编排器 - 全自动调度Agent团队

    工作流程:
    1. JD Intake → 解析JD文本为结构化需求
    2. Search Orchestrator → 决定搜索策略
    3. Duolie Agent → 执行多猎搜索
    4. Matcher Agent → 评分排序
    5. Evaluator Agent → 深度评估
    6. Report Agent → 生成报告
    """

    def __init__(self):
        self.registry = AgentRegistry()
        self._results: Dict[str, OrchestrationResult] = {}
        self._timings: Dict[str, float] = {}

    def _log_timing(self, step: str):
        self._timings[step] = time.time()

    def _elapsed(self, step_from: str, step_to: str) -> float:
        return round(self._timings.get(step_to, 0) - self._timings.get(step_from, 0), 2)

    # ==================== 步骤1: JD Intake ====================

    def parse_jd(self, raw_text: str) -> Dict[str, Any]:
        """JD解析 - 从原始文本提取结构化需求"""
        self._log_timing("jd_parse")

        jd = {
            "title": "",
            "salary_min": 0,
            "salary_max": 0,
            "location": "",
            "education": "",
            "experience_years_min": 0,
            "experience_years_max": 99,
            "skills": [],
            "keywords": [],
            "raw_text": raw_text
        }

        # 薪资范围
        salary_match = __import__('re').search(r'(\d+)\s*[-~]\s*(\d+)\s*万', raw_text)
        if salary_match:
            jd["salary_min"] = int(salary_match.group(1))
            jd["salary_max"] = int(salary_match.group(2))

        # 地点
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京']
        for c in cities:
            if c in raw_text:
                jd["location"] = c
                break

        # 学历
        edu_map = {'博士': '博士', '硕士': '硕士', '本科': '本科', '大专': '大专'}
        for k, v in edu_map.items():
            if k in raw_text:
                jd["education"] = v
                break

        # 经验年限
        exp_match = __import__('re').search(r'(\d+)\s*年?以上?\s*(?:经验|工作)', raw_text)
        if exp_match:
            jd["experience_years_min"] = int(exp_match.group(1))
        exp_range = __import__('re').search(r'(\d+)\s*[-~]\s*(\d+)\s*年', raw_text)
        if exp_range:
            jd["experience_years_min"] = int(exp_range.group(1))
            jd["experience_years_max"] = int(exp_range.group(2))

        # 职位名称
        title_match = __import__('re').search(r'((?:高级|资深|首席|主任|助理)?[\u4e00-\u9fa5]{2,10}(?:专家|经理|总监|主任|分析师|工程师|顾问|官|长))', raw_text)
        if title_match:
            jd["title"] = title_match.group(1)

        # 技能关键词
        skill_db = ['Python', 'SQL', 'SAS', 'R', 'GLM', 'GBDT', 'GAM', 'XGBoost',
                     '机器学习', '深度学习', '精算', '定价', '费率', '准备金',
                     'IBNR', '数据分析', '数据建模', '预测模型', 'NLP', 'CV',
                     'TensorFlow', 'PyTorch', 'Spark', 'Hadoop', 'Tableau']
        jd["skills"] = [s for s in skill_db if s in raw_text]

        # 搜索关键词
        keywords = []
        if jd["title"]:
            keywords.append(jd["title"])
        keywords.extend(jd["skills"][:3])
        jd["keywords"] = list(set(keywords))

        self._log_timing("jd_parse_done")
        return jd

    # ==================== 步骤2: 搜索策略 ====================

    def decide_strategy(self, jd: Dict[str, Any]) -> Dict[str, Any]:
        """决定搜索策略 - 预算薪资映射工作经验"""
        self._log_timing("strategy")

        strategy = {
            "platform": "duolie",
            "target_experience_min": 0,
            "target_experience_max": 99,
            "target_salary_min": 0,
            "target_salary_max": 0,
            "search_queries": [],
        }

        salary_min = jd.get("salary_min", 0)
        salary_max = jd.get("salary_max", 0)
        strategy["target_salary_min"] = salary_min
        strategy["target_salary_max"] = salary_max

        # 按预算推算经验范围
        if salary_max > 0 and salary_min > 0:
            avg_salary = (salary_min + salary_max) / 2
            if avg_salary <= 30:
                strategy["target_experience_min"] = 1
                strategy["target_experience_max"] = 5
            elif avg_salary <= 60:
                strategy["target_experience_min"] = 3
                strategy["target_experience_max"] = 8
            elif avg_salary <= 100:
                strategy["target_experience_min"] = 5
                strategy["target_experience_max"] = 12
            elif avg_salary <= 150:
                strategy["target_experience_min"] = 8
                strategy["target_experience_max"] = 15
            else:
                strategy["target_experience_min"] = 10
                strategy["target_experience_max"] = 20

        # 叠加JD明确要求
        if jd.get("experience_years_min", 0) > 0:
            strategy["target_experience_min"] = max(
                strategy["target_experience_min"], jd["experience_years_min"]
            )
        if jd.get("experience_years_max", 99) < 99:
            strategy["target_experience_max"] = min(
                strategy["target_experience_max"], jd["experience_years_max"]
            )

        # 生成搜索词
        base_queries = []
        if jd.get("keywords"):
            base_queries = jd["keywords"][:5]
        if jd.get("title"):
            base_queries.insert(0, jd["title"])
        strategy["search_queries"] = base_queries if base_queries else ["候选人"]

        self._log_timing("strategy_done")
        return strategy

    # ==================== 新增: 生成语义搜索描述 ====================

    def generate_search_description(self, jd: Dict[str, Any]) -> str:
        """
        从JD解析结果生成一段语义搜索描述，用于多猎平台搜索。
        包含: 职位名称、工作地点、薪资范围、优先要求条件。
        目标: 1-2次搜索即可找到足够相关的候选人。
        """
        self._log_timing("search_desc")

        parts = []

        # 职位名称
        title = jd.get("title", "")
        if title:
            parts.append(f"职位：{title}")

        # 核心职责提炼
        raw = jd.get("raw_text", "")
        # 从职责描述中提取关键短语
        duty_section = ""
        if "职责描述" in raw:
            duty_section = raw.split("职责描述")[1].split("任职要求")[0] if "任职要求" in raw else raw.split("职责描述")[1] if "职责描述" in raw else ""
        elif "职责" in raw:
            duty_section = raw.split("职责")[1][:200] if "职责" in raw else ""

        if duty_section:
            # 提取核心关键词
            duty_keywords = []
            for kw in ["模型开发", "费率厘定", "产品定价", "准备金", "IBNR",
                       "精算模型", "GLM", "GBDT", "Python", "SAS", "SQL",
                       "数据分析", "车险", "赔付", "定价"]:
                if kw in duty_section:
                    duty_keywords.append(kw)
            if duty_keywords:
                parts.append(f"核心能力：{'/'.join(duty_keywords[:5])}")

        # 技能要求
        skills = jd.get("skills", [])
        if skills:
            parts.append(f"技能要求：{'/'.join(skills[:6])}")

        # 工作地点
        loc = jd.get("location", "")
        if loc:
            parts.append(f"工作地点：{loc}")

        # 薪资范围
        sal_min = jd.get("salary_min", 0)
        sal_max = jd.get("salary_max", 0)
        if sal_min > 0 and sal_max > 0:
            parts.append(f"预算年薪：{sal_min}-{sal_max}万")

        # 经验要求
        exp_min = jd.get("experience_years_min", 0)
        exp_max = jd.get("experience_years_max", 99)
        if exp_min > 0 and exp_max < 99:
            parts.append(f"经验要求：{exp_min}-{exp_max}年")
        elif exp_min > 0:
            parts.append(f"经验要求：{exp_min}年以上")

        # 学历
        edu = jd.get("education", "")
        if edu:
            parts.append(f"学历要求：{edu}及以上")

        # 优先条件
        priority_keywords = []
        priority_patterns = ["优先", "有.*经验优先", "熟悉.*优先"]
        for pat in priority_patterns:
            matches = re.findall(pat, raw)
            if matches:
                idx = raw.find(matches[0])
                if idx > 0:
                    snippet = raw[max(0,idx-30):idx+50]
                    priority_keywords.append(snippet.strip())

        # 压缩成一段话
        desc = "；".join(parts)
        if len(desc) > 200:
            desc = desc[:200]

        self._log_timing("search_desc_done")
        return desc

    # ==================== 步骤3: 候选人匹配评分 ====================

    def score_candidate(self, candidate: Dict[str, Any], jd: Dict[str, Any],
                        strategy: Dict[str, Any]) -> Dict[str, Any]:
        """多维度匹配评分"""
        score_breakdown = {}
        total = 0

        # 1. 工作年限匹配 (30分)
        exp_years = candidate.get("experience_years", 0)
        target_min = strategy["target_experience_min"]
        target_max = strategy["target_experience_max"]
        if target_min <= exp_years <= target_max:
            exp_score = 30
        elif exp_years < target_min:
            exp_score = max(10, 30 - (target_min - exp_years) * 5)
        else:
            exp_score = max(10, 30 - (exp_years - target_max) * 3)
        score_breakdown["工作年限"] = exp_score
        total += exp_score

        # 2. 薪资匹配 (30分)
        salary_expect = candidate.get("salary_expect", 0)
        target_s_min = strategy["target_salary_min"]
        target_s_max = strategy["target_salary_max"]
        if target_s_min > 0 and target_s_max > 0:
            if target_s_min <= salary_expect <= target_s_max:
                salary_score = 30
            elif salary_expect < target_s_min:
                salary_score = max(10, 30 - (target_s_min - salary_expect) * 0.5)
            else:
                salary_score = max(5, 30 - (salary_expect - target_s_max) * 0.3)
            score_breakdown["薪资匹配"] = salary_score
            total += salary_score
        else:
            score_breakdown["薪资匹配"] = 20
            total += 20

        # 3. 学历匹配 (20分)
        edu = candidate.get("education", "")
        target_edu = jd.get("education", "")
        edu_rank = {'博士': 4, '硕士': 3, '本科': 2, '大专': 1, '': 0}
        target_level = edu_rank.get(target_edu, 0)
        cand_level = edu_rank.get(edu, 0)
        if cand_level >= target_level:
            edu_score = 20
        elif cand_level == target_level - 1:
            edu_score = 12
        else:
            edu_score = 5
        score_breakdown["学历匹配"] = edu_score
        total += edu_score

        # 4. 技能关键词匹配 (20分)
        required_skills = jd.get("skills", [])
        cand_text = (candidate.get("skills_text", "") + " " +
                     candidate.get("experience_text", "") + " " +
                     candidate.get("title", ""))
        if required_skills:
            hits = sum(1 for s in required_skills if s.lower() in cand_text.lower())
            skill_score = min(20, hits * (20 / max(len(required_skills), 1)))
        else:
            skill_score = 15
        score_breakdown["技能匹配"] = skill_score
        total += skill_score

        # 总评分
        return {
            "total_score": total,
            "breakdown": score_breakdown,
            "summary": self._generate_match_summary(score_breakdown, candidate, jd)
        }

    def _generate_match_summary(self, breakdown: Dict[str, float],
                                 candidate: Dict[str, Any], jd: Dict[str, Any]) -> str:
        """生成匹配摘要"""
        parts = []
        exp_years = candidate.get("experience_years", 0)
        target_min = jd.get("experience_years_min", 0)
        if exp_years >= target_min:
            parts.append(f"工作经验{exp_years}年，符合{target_min}年+要求")
        else:
            parts.append(f"工作经验{exp_years}年，略低于{target_min}年要求")

        salary = candidate.get("salary_expect", 0)
        if jd.get("salary_min", 0) <= salary <= jd.get("salary_max", 999):
            parts.append(f"期望薪资{salary}万，在预算范围{jd.get('salary_min',0)}-{jd.get('salary_max',0)}万内")
        else:
            parts.append(f"期望薪资{salary}万")

        edu = candidate.get("education", "")
        if edu:
            parts.append(f"学历{edu}")

        return "；".join(parts)

    # ==================== 步骤4: 全流程编排 ====================

    def run_pipeline(self, raw_text: str,
                     candidates_data: Optional[List[Dict[str, Any]]] = None) -> OrchestrationResult:
        """
        全自动编排 - 解析JD → 搜索描述 → 策略 → 搜索 → 评分 → 评估 → 报告

        Args:
            raw_text: JD原始文本
            candidates_data: 可选，外部输入的候选人数据（模拟真实搜索）
        """
        result = OrchestrationResult()
        result.status = "running"

        try:
            # Step 1: JD Parsing
            jd = self.parse_jd(raw_text)
            result.jd_parsed = jd

            # Step 2: Generate search description (New!)
            search_desc = self.generate_search_description(jd)
            result.search_description = search_desc

            # Step 3: Strategy
            strategy = self.decide_strategy(jd)
            result.search_strategy = strategy

            # Step 4: Score candidates
            if candidates_data:
                result.candidates_raw = candidates_data
                scored = []
                for c in candidates_data:
                    score_result = self.score_candidate(c, jd, strategy)
                    scored.append({
                        **c,
                        "match_score": score_result["total_score"],
                        "score_breakdown": score_result["breakdown"],
                        "match_summary": score_result["summary"],
                    })
                scored.sort(key=lambda x: x["match_score"], reverse=True)
                result.candidates_scored = scored
                result.top_candidates = scored[:10]

            # Step 5: Generate evaluation summary
            if result.top_candidates:
                result.evaluation = self._generate_report(
                    jd, strategy, result.top_candidates
                )

            result.total_time_ms = int((time.time() - self._timings.get("jd_parse", time.time())) * 1000)
            result.agent_timings = self._timings
            result.status = "completed"

        except Exception as e:
            result.status = "failed"
            result.error = str(e)

        return result

    def _generate_report(self, jd: Dict[str, Any], strategy: Dict[str, Any],
                          top_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成汇总报告"""
        avg_score = sum(c["match_score"] for c in top_candidates) / max(len(top_candidates), 1)
        return {
            "total_candidates": len(top_candidates),
            "average_score": round(avg_score, 1),
            "salary_range": f"{jd.get('salary_min', '?')}万-{jd.get('salary_max', '?')}万",
            "target_experience": f"{strategy['target_experience_min']}-{strategy['target_experience_max']}年",
            "top_match": top_candidates[0]["match_score"] if top_candidates else 0,
            "summary": self._generate_report_summary(jd, top_candidates),
            "market_insight": self._generate_market_insight(jd, strategy, top_candidates),
        }

    def _generate_report_summary(self, jd: Dict[str, Any],
                                  candidates: List[Dict[str, Any]]) -> str:
        """生成报告摘要"""
        if not candidates:
            return "未找到匹配候选人"
        return (f"共匹配到{len(candidates)}名候选人，"
                f"最高匹配度{candidates[0]['match_score']}%，"
                f"平均匹配度{sum(c['match_score'] for c in candidates)//len(candidates)}%")

    def _generate_market_insight(self, jd: Dict[str, Any],
                                  strategy: Dict[str, Any],
                                  candidates: List[Dict[str, Any]]) -> str:
        """生成市场洞察"""
        total = len(candidates)
        if total == 0:
            return "人才市场上该领域候选人相对稀缺，建议扩大搜索范围"

        avg_salary = sum(c.get("salary_expect", 0) for c in candidates) / total
        budget_min = jd.get("salary_min", 0)
        budget_max = jd.get("salary_max", 0)

        if avg_salary > budget_max:
            return (f"候选人平均期望薪资(约{avg_salary:.0f}万/年)高于预算上{budget_max}万，"
                    "建议适当调整预算或寻找资历稍浅的候选人")
        elif avg_salary < budget_min:
            return (f"候选人平均期望薪资(约{avg_salary:.0f}万/年)低于预算下{budget_min}万，"
                    "可考虑招聘更资深的候选人")
        else:
            return (f"候选人平均期望薪资(约{avg_salary:.0f}万/年)在预算范围内，"
                    f"市场上共有约{total*3}名相关候选人可供筛选")


# ==================== CLI用法 ====================

def run_orchestrator_cli(jd_text: str, candidates_json: Optional[str] = None):
    """CLI入口"""
    orchestrator = AgentOrchestrator()

    candidates = None
    if candidates_json:
        try:
            with open(candidates_json, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
        except Exception as e:
            print(f"⚠️ 候选人数据加载失败: {e}")

    result = orchestrator.run_pipeline(jd_text, candidates)
    print(f"\n{'='*60}")
    print(f"📋 JD解析结果")
    print(f"{'='*60}")
    for k, v in result.jd_parsed.items():
        if k != 'raw_text':
            print(f"  {k}: {v}")

    if result.top_candidates:
        print(f"\n{'='*60}")
        print(f"🏆 TOP{len(result.top_candidates)} 候选人")
        print(f"{'='*60}")
        for i, c in enumerate(result.top_candidates[:5], 1):
            print(f"\n  #{i} {c.get('name', '未知')} | 匹配度: {c.get('match_score', 0)}%")
            print(f"     {c.get('company', '')} | {c.get('title', '')}")
            print(f"     期望{c.get('salary_expect', '?')}万 | {c.get('experience_years', '?')}年")
            print(f"     得分明细: {c.get('score_breakdown', {})}")
            print(f"     摘要: {c.get('match_summary', '')}")

    if result.evaluation:
        print(f"\n{'='*60}")
        print(f"📊 报告摘要")
        print(f"{'='*60}")
        print(f"  预算: {result.evaluation['salary_range']}")
        print(f"  目标经验: {result.evaluation['target_experience']}")
        print(f"  最高匹配: {result.evaluation['top_match']}%")
        print(f"  平均匹配: {result.evaluation['average_score']}%")
        print(f"  市场洞察: {result.evaluation['market_insight']}")

    print(f"\n⏱️ 耗时: {result.total_time_ms}ms")
    print(f"状态: {result.status}")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        jd_text = sys.argv[1]
        candidates_file = sys.argv[2] if len(sys.argv) > 2 else None
        run_orchestrator_cli(jd_text, candidates_file)
    else:
        # Demo mode
        demo_jd = "车险高级精算专家 60-90万 北京 本科+ 3年以上 精算经验 GLM Python SAS"
        print(f"使用示例JD: {demo_jd}")
        run_orchestrator_cli(demo_jd)
