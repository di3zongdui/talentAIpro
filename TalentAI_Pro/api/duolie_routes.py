"""
多猎平台候选人搜索 API
对接 duolie_scraper 实现真实候选人搜索
"""

import subprocess
import json
import sqlite3
import os
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
    search_value: str = ""       # 搜索关键词或公司名
    min_years: int = 0            # 最小工作年限
    min_salary: int = 0          # 最小期望薪资(K)
    max_salary: int = 999        # 最大期望薪资(K)
    education: Optional[List[str]] = None  # 学历要求
    keywords: Optional[List[str]] = None    # 简历关键词
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
            script = generate_search_script(request)
            return {
                "success": True,
                "source": "script",
                "total": 0,
                "candidates": [],
                "script": script,
                "message": "数据库暂无数据，请先在浏览器中执行搜索脚本"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_candidates_from_db(request: DuolieSearchRequest) -> List[Dict]:
    """从数据库查询候选人"""
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
        where_clauses.append("(search_keyword LIKE ? OR current_title LIKE ? OR current_company LIKE ?)")
        params.extend([f"%{request.search_value}%"] * 3)

    if request.min_years > 0:
        where_clauses.append("work_years >= ?")
        params.append(request.min_years)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT name, gender, age, current_company, current_title, work_years,
               education, current_city, expected_salary, current_salary,
               latest_update, match_score, detail_url
        FROM candidates
        WHERE {where_sql}
        ORDER BY match_score DESC, work_years DESC
        LIMIT {request.top_n}
    """

    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()

    candidates = []
    for row in rows:
        candidates.append({
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
            "detail_url": row[12] or ""
        })

    return candidates


def generate_search_script(request: DuolieSearchRequest) -> Dict[str, Any]:
    """生成浏览器搜索脚本"""
    if request.search_type == "company":
        commands = [
            f'browser-use --profile openclaw open https://www.duolie.com/newtalent/talentlist',
            'browser-use state',
            f'browser-use input 11 "{request.search_value}"',
            'browser-use click 3'
        ]
    else:
        commands = [
            f'browser-use --profile openclaw open https://www.duolie.com/newtalent/talentlist',
            'browser-use state',
            f'browser-use input 2 "{request.search_value}"',
            'browser-use keys Enter'
        ]

    extract_script = """
(function() {
    const items = document.querySelectorAll('.talent-item, .candidate-item, [class*="talent"][class*="item"]');
    return JSON.stringify(Array.from(items).map(item => ({
        name: item.querySelector('.name')?.textContent?.trim() || '',
        current_company: item.querySelector('.company')?.textContent?.trim() || '',
        current_title: item.querySelector('.title')?.textContent?.trim() || '',
        work_years: item.querySelector('.experience')?.textContent?.trim() || '',
        education: item.querySelector('.education')?.textContent?.trim() || '',
        expected_salary: item.querySelector('.expected-salary')?.textContent?.trim() || '',
        detail_url: item.querySelector('a[href*="talent"]')?.href || ''
    })));
})()
""".replace('"', '\\"').replace('\n', ' ')

    return {
        "commands": commands,
        "extract_script": extract_script,
        "next_page_script": "document.querySelector('.next, [class*=\"next\"]')?.click()"
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
            search_type == "company" and search_value or None,
            search_type == "keyword" and search_value or None,
            "duolie",
            cand.get("detail_url"),
            json.dumps(cand, ensure_ascii=False),
            __import__("datetime").datetime.now().isoformat()
        ))
        saved += 1

    c.execute('''
        INSERT INTO search_records (search_type, search_value, total_found, total_saved, searched_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (search_type, search_value, len(candidates), saved,
          __import__("datetime").datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {"success": True, "saved": saved, "total": len(candidates)}
