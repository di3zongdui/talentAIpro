"""
多猎平台候选人搜索 API
对接 duolie_scraper 实现真实候选人搜索
"""

import subprocess
import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="/api/duolie", tags=["多猎搜索"])

# 数据库路径
SKILL_DIR = Path(__file__).parent.parent.parent / ".workbuddy" / "skills" / "cgl-duolie-search"
DB_PATH = SKILL_DIR / "candidates.db"


class DuolieSearchRequest(BaseModel):
    """多猎搜索请求"""
    search_type: str = "keyword"  # "company" 或 "keyword"
    search_value: str = ""        # 语义搜索描述
    min_years: int = 0            # 最小工作年限
    min_salary: int = 0           # 最小期望薪资(万)
    max_salary: int = 999        # 最大期望薪资(万)
    location: Optional[str] = None # 工作地点
    education: Optional[List[str]] = None  # 学历要求
    keywords: Optional[List[str]] = None    # 简历关键词
    jd_info: Optional[Dict[str, Any]] = None  # JD完整信息(用于评分)
    top_n: int = 50              # 返回前N个


class CandidateResult(BaseModel):
    """候选人结果"""
    name: str = ""
    gender: str = ""
    age: int = 0
    current_company: str = ""
    current_title: str = ""
    work_years: int = 0
    education: str = ""
    current_city: str = ""
    expected_salary: str = ""
    current_salary: str = ""
    latest_update: str = ""
    match_score: float = 0
    detail_url: str = ""


@router.post("/search")
async def duolie_search(request: DuolieSearchRequest) -> Dict[str, Any]:
    """
    多猎候选人搜索
    从数据库查询已保存的候选人，或生成搜索脚本
    """
    try:
        # 先从数据库查询已存在的候选人
        candidates = get_candidates_from_db(request)

        if candidates:
            return {
                "success": True,
                "source": "database",
                "total": len(candidates),
                "candidates": candidates[:request.top_n],
                "message": f"从数据库返回 {len(candidates[:request.top_n])} 位候选人"
            }
        else:
            # 生成浏览器搜索脚本
            script = generate_browser_script(request)
            return {
                "success": True,
                "source": "script",
                "total": 0,
                "candidates": [],
                "browser_script": script,
                "message": "数据库暂无数据，请使用 agent-browser 工具执行搜索脚本"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_candidates_from_db(request: DuolieSearchRequest) -> List[Dict]:
    """从数据库查询候选人（带多维度评分）"""
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 构建查询
    where_clauses = []
    params = []

    if request.search_type == "company" and request.search_value:
        where_clauses.append("search_company LIKE ?")
        params.append(f"%{request.search_value}%")
    elif request.search_type == "keyword" and request.search_value:
        # 语义搜索：匹配关键词或职位或公司
        search_terms = request.search_value.split()
        keyword_conditions = []
        for term in search_terms:
            keyword_conditions.append("(search_keyword LIKE ? OR current_title LIKE ? OR current_company LIKE ?)")
            params.extend([f"%{term}%"] * 3)
        if keyword_conditions:
            where_clauses.append(" OR ".join(keyword_conditions))

    # 工作年限筛选
    if request.min_years > 0:
        where_clauses.append("work_years >= ?")
        params.append(request.min_years)

    # 地点筛选
    if request.location:
        where_clauses.append("current_city LIKE ?")
        params.append(f"%{request.location}%")

    # 学历筛选
    if request.education and len(request.education) > 0:
        edu_conditions = []
        for edu in request.education:
            edu_conditions.append("education LIKE ?")
            params.append(f"%{edu}%")
        if edu_conditions:
            where_clauses.append(" OR ".join(edu_conditions))

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT name, gender, age, current_company, current_title, work_years,
               education, current_city, expected_salary, current_salary,
               latest_update, match_score, detail_url, raw_data
        FROM candidates
        WHERE {where_sql}
        ORDER BY match_score DESC, work_years DESC
        LIMIT 200
    """

    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()

    candidates = []
    for row in rows:
        cand = {
            "name": row[0] or "",
            "gender": row[1] or "",
            "age": row[2] or 0,
            "current_company": row[3] or "",
            "current_title": row[4] or "",
            "work_years": row[5] or 0,
            "education": row[6] or "",
            "current_city": row[7] or "",
            "expected_salary": row[8] or "",
            "current_salary": row[9] or "",
            "latest_update": row[10] or "",
            "match_score": row[11] or 0,
            "detail_url": row[12] or "",
            "raw_data": row[13] or ""
        }

        # 薪资过滤（Python层处理）
        if request.min_salary > 0:
            salary_num = extract_salary_number(cand["expected_salary"])
            if salary_num < request.min_salary:
                continue
        if request.max_salary < 999:
            salary_num = extract_salary_number(cand["expected_salary"])
            if salary_num > request.max_salary:
                continue

        # 多维度评分
        cand["match_score"] = calculate_match_score(cand, request)
        candidates.append(cand)

    # 按评分排序
    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates[:request.top_n]


def extract_salary_number(salary_str: str) -> int:
    """从薪资字符串提取数字"""
    if not salary_str:
        return 0
    import re
    match = re.search(r'(\d+)', salary_str)
    return int(match.group(1)) if match else 0


def calculate_match_score(cand: Dict, request: DuolieSearchRequest) -> float:
    """多维度匹配评分算法"""
    score = 0
    max_score = 100

    jd_info = request.jd_info or {}

    # 1. 工作年限匹配 (30分)
    years_score = 30
    if jd_info.get("experienceMin"):
        required_years = jd_info["experienceMin"]
        actual_years = cand.get("work_years", 0)
        if actual_years >= required_years:
            # 超过要求，加分但有上限
            extra = min((actual_years - required_years) * 2, 10)
            years_score = 30 + extra
    score += min(years_score, 40)  # 上限40分

    # 2. 薪资匹配 (25分)
    salary_score = 25
    if jd_info.get("salaryMin") and jd_info.get("salaryMax"):
        cand_salary = extract_salary_number(cand.get("expected_salary", ""))
        if cand_salary > 0:
            if jd_info["salaryMin"] <= cand_salary <= jd_info["salaryMax"]:
                salary_score = 25  # 完全匹配
            elif cand_salary < jd_info["salaryMin"]:
                salary_score = 15  # 低于预算，性价比高
            else:
                salary_score = 10  # 高于预算
    score += salary_score

    # 3. 技能匹配 (25分)
    skill_score = 0
    jd_skills = jd_info.get("skills", [])
    cand_title = cand.get("current_title", "")
    cand_company = cand.get("current_company", "")

    if jd_skills:
        # 检查标题/公司是否包含技能关键词
        combined = cand_title + cand_company
        matched = sum(1 for skill in jd_skills if skill in combined)
        skill_score = min(matched * 8, 25)  # 每个技能8分，上限25分
    score += skill_score

    # 4. 学历匹配 (10分)
    edu_score = 0
    jd_edu = jd_info.get("education", "")
    cand_edu = cand.get("education", "")

    edu_levels = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
    if jd_edu and cand_edu:
        jd_level = edu_levels.get(jd_edu, 0)
        cand_level = edu_levels.get(cand_edu, 0)
        if cand_level >= jd_level:
            edu_score = 10  # 满足要求
        else:
            edu_score = 5  # 低于要求
    elif not jd_edu:
        edu_score = 8  # JD无学历要求
    score += edu_score

    # 5. 地点匹配 (10分)
    location_score = 5  # 默认部分匹配
    if jd_info.get("location") and cand.get("current_city"):
        if jd_info["location"] in cand["current_city"]:
            location_score = 10  # 完全匹配
    elif not jd_info.get("location"):
        location_score = 8  # JD无地点要求
    score += location_score

    return round(score, 1)


def generate_browser_script(request: DuolieSearchRequest) -> Dict[str, Any]:
    """生成 agent-browser 浏览器搜索脚本"""
    search_value = request.search_value or "人工智能工程师"

    # 生成 Base64 编码的 JS 脚本（避免转义问题）
    extract_js = """
(function() {
    const items = document.querySelectorAll('.talent-item, .candidate-item, [class*="talent"][class*="item"]');
    if (items.length === 0) {
        // 尝试更通用的选择器
        const allCards = document.querySelectorAll('[class*="card"], [class*="list-item"]');
        if (allCards.length > 0) {
            return JSON.stringify(Array.from(allCards).slice(0, 20).map((item, idx) => ({
                name: item.querySelector('[class*="name"]')?.textContent?.trim() || `候选人${idx+1}`,
                current_company: item.querySelector('[class*="company"]')?.textContent?.trim() || '',
                current_title: item.querySelector('[class*="title"]')?.textContent?.trim() || '',
                work_years: item.querySelector('[class*="exp"]')?.textContent?.trim() || '',
                education: item.querySelector('[class*="edu"]')?.textContent?.trim() || '',
                expected_salary: item.querySelector('[class*="salary"]')?.textContent?.trim() || '',
                detail_url: item.querySelector('a')?.href || ''
            })));
        }
    }
    return JSON.stringify(Array.from(items).map((item, idx) => ({
        name: item.querySelector('.name, [class*="name"]')?.textContent?.trim() || `候选人${idx+1}`,
        current_company: item.querySelector('.company, [class*="company"]')?.textContent?.trim() || '',
        current_title: item.querySelector('.title, [class*="title"]')?.textContent?.trim() || '',
        work_years: item.querySelector('.experience, [class*="exp"]')?.textContent?.trim() || '',
        education: item.querySelector('.education, [class*="edu"]')?.textContent?.trim() || '',
        expected_salary: item.querySelector('.expected-salary, [class*="salary"]')?.textContent?.trim() || '',
        detail_url: item.querySelector('a[href*="talent"]')?.href || ''
    })));
})()
"""
    import base64
    extract_b64 = base64.b64encode(extract_js.encode('utf-8')).decode('utf-8')

    # agent-browser 命令格式
    commands = [
        f'agent-browser -b openclaw open "https://www.duolie.com/newtalent/talentlist"',
        'agent-browser -b openclaw wait 3000',
        f'agent-browser -b openclaw type "input[type=\\"text\\"], input[type=\\"search\\"]" "{search_value}"',
        'agent-browser -b openclaw press Enter',
        'agent-browser -b openclaw wait 2000',
        f'agent-browser -b openclaw eval "{extract_b64}"'
    ]

    return {
        "commands": commands,
        "extract_script_base64": extract_b64,
        "search_guide": f"请在多猎平台搜索框输入：{search_value}",
        "note": "使用 agent-browser 自动化工具，确保已安装 agent-browser v0.27.0+"
    }


@router.get("/history")
async def get_search_history() -> Dict[str, Any]:
    """获取搜索历史"""
    if not DB_PATH.exists():
        return {"success": True, "history": []}

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    c.execute("""
        SELECT id, search_type, search_value, total_found, total_saved, searched_at
        FROM search_records
        ORDER BY searched_at DESC
        LIMIT 50
    """)

    rows = c.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "search_type": row[1],
            "search_value": row[2],
            "total_found": row[3],
            "total_saved": row[4],
            "searched_at": row[5]
        })

    return {"success": True, "history": history}


@router.post("/save-candidates")
async def save_candidates(candidates: List[Dict], search_type: str, search_value: str) -> Dict[str, Any]:
    """保存候选人到数据库"""
    import os
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 确保表存在
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, gender TEXT, age INTEGER, current_company TEXT,
            current_title TEXT, work_years INTEGER, education TEXT,
            current_city TEXT, expected_salary TEXT, current_salary TEXT,
            latest_update TEXT, match_score REAL, search_company TEXT,
            search_keyword TEXT, source TEXT, detail_url TEXT,
            raw_data TEXT, created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_type TEXT, search_value TEXT, total_found INTEGER,
            total_saved INTEGER, searched_at TEXT
        )
    ''')

    saved = 0
    for cand in candidates:
        if not cand.get("name"):
            continue

        c.execute("SELECT id FROM candidates WHERE name=? AND current_company=?",
                  (cand.get("name"), cand.get("current_company")))
        if c.fetchone():
            continue

        # 确定搜索公司和关键词字段
        search_company_val = search_value if search_type == "company" else None
        search_keyword_val = search_value if search_type == "keyword" else None

        c.execute('''
            INSERT INTO candidates (
                name, gender, age, current_company, current_title, work_years,
                education, current_city, expected_salary, current_salary,
                latest_update, match_score, search_company, search_keyword,
                source, detail_url, raw_data, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cand.get("name"), cand.get("gender"), cand.get("age"),
            cand.get("current_company"), cand.get("current_title"),
            cand.get("work_years"), cand.get("education"),
            cand.get("current_city"), cand.get("expected_salary"),
            cand.get("current_salary"), cand.get("latest_update"),
            cand.get("match_score", 0),
            search_company_val,
            search_keyword_val,
            "duolie",
            cand.get("detail_url", ""),
            json.dumps(cand, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        saved += 1

    c.execute('''
        INSERT INTO search_records (search_type, search_value, total_found, total_saved, searched_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (search_type, search_value, len(candidates), saved,
           datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {"success": True, "saved": saved, "total": len(candidates)}
