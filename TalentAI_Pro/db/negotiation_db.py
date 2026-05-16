"""
谈判会话数据库模块
====================

提供谈判会话和消息的持久化存储功能。

Usage:
    from db.negotiation_db import NegotiationDB

    db = NegotiationDB()

    # 创建会话
    db.create_session("neg-123", candidate_info="张三", company_offer="22K*14")

    # 添加消息
    db.add_message("neg-123", "hr", "您好，我们给您22K的offer")

    # 获取会话
    session = db.get_session("neg-123")

    # 获取消息历史
    messages = db.get_messages("neg-123")

    # 更新会话状态
    db.update_session("neg-123", status="completed", final_deal="25K*14")
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'talentai.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """上下文管理器：自动关闭连接"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


class NegotiationDB:
    """谈判会话数据库操作类"""

    @staticmethod
    def init_db():
        """确保数据库表已创建"""
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS negotiation_sessions (
                    id TEXT PRIMARY KEY,
                    candidate_id TEXT,
                    job_id TEXT,
                    candidate_info TEXT,
                    company_offer TEXT,
                    tone TEXT,
                    status TEXT DEFAULT 'active',
                    final_deal TEXT,
                    rounds INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS negotiation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    round INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES negotiation_sessions(id)
                )
            ''')
            conn.commit()

    @staticmethod
    def create_session(
        session_id: str,
        candidate_id: str = None,
        job_id: str = None,
        candidate_info: str = "",
        company_offer: str = "",
        tone: str = "moderate"
    ) -> bool:
        """创建新谈判会话"""
        NegotiationDB.init_db()
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO negotiation_sessions
                (id, candidate_id, job_id, candidate_info, company_offer, tone, status, rounds)
                VALUES (?, ?, ?, ?, ?, ?, 'active', 0)
            ''', (session_id, candidate_id, job_id, candidate_info, company_offer, tone))
            conn.commit()
            return True

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话详情"""
        with get_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM negotiation_sessions WHERE id = ?', (session_id,))
            row = c.fetchone()
            if row:
                return dict(row)
            return None

    @staticmethod
    def update_session(
        session_id: str,
        status: str = None,
        final_deal: str = None,
        rounds: int = None
    ) -> bool:
        """更新会话状态"""
        with get_db() as conn:
            c = conn.cursor()
            updates = []
            params = []

            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if final_deal is not None:
                updates.append("final_deal = ?")
                params.append(final_deal)
            if rounds is not None:
                updates.append("rounds = ?")
                params.append(rounds)

            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(session_id)
                sql = f"UPDATE negotiation_sessions SET {', '.join(updates)} WHERE id = ?"
                c.execute(sql, params)
                conn.commit()
            return True

    @staticmethod
    def add_message(
        session_id: str,
        role: str,
        content: str,
        round_num: int = 0
    ) -> bool:
        """添加谈判消息"""
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO negotiation_messages (session_id, role, content, round)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, round_num))

            # 更新会话轮次
            c.execute('''
                UPDATE negotiation_sessions
                SET rounds = MAX(rounds, ? + 1), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (round_num, session_id))
            conn.commit()
            return True

    @staticmethod
    def get_messages(session_id: str) -> List[Dict[str, Any]]:
        """获取会话的所有消息"""
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT * FROM negotiation_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
            ''', (session_id,))
            return [dict(row) for row in c.fetchall()]

    @staticmethod
    def get_session_with_messages(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话及其完整消息历史"""
        session = NegotiationDB.get_session(session_id)
        if session:
            messages = NegotiationDB.get_messages(session_id)
            session['messages'] = messages
        return session

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """删除会话及其所有消息"""
        with get_db() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM negotiation_messages WHERE session_id = ?', (session_id,))
            c.execute('DELETE FROM negotiation_sessions WHERE id = ?', (session_id,))
            conn.commit()
            return True

    @staticmethod
    def list_sessions(
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """列出谈判会话（分页）"""
        with get_db() as conn:
            c = conn.cursor()
            if status:
                c.execute('''
                    SELECT * FROM negotiation_sessions
                    WHERE status = ?
                    ORDER BY updated_at DESC
                    LIMIT ? OFFSET ?
                ''', (status, limit, offset))
            else:
                c.execute('''
                    SELECT * FROM negotiation_sessions
                    ORDER BY updated_at DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            return [dict(row) for row in c.fetchall()]

    @staticmethod
    def search_sessions(keyword: str) -> List[Dict[str, Any]]:
        """搜索谈判会话"""
        with get_db() as conn:
            c = conn.cursor()
            pattern = f"%{keyword}%"
            c.execute('''
                SELECT * FROM negotiation_sessions
                WHERE candidate_info LIKE ? OR company_offer LIKE ? OR final_deal LIKE ?
                ORDER BY updated_at DESC
                LIMIT 50
            ''', (pattern, pattern, pattern))
            return [dict(row) for row in c.fetchall()]
