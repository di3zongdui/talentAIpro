"""
Negotiation History Storage - 谈判历史持久化模块
=================================================
将谈判记录存储到SQLite数据库，支持查询和历史回溯

Usage:
    from skills.negotiation.history_storage import NegotiationHistoryStorage

    storage = NegotiationHistoryStorage()
    storage.save_negotiation_round({
        "negotiation_id": "neg_001",
        "offer_id": "offer_123",
        "round": 1,
        "perspective": "recruiter",
        "company_offer": {...},
        "candidate_expectation": {...},
        "result": {...}
    })
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'talentai.db')


@dataclass
class NegotiationRecord:
    """谈判记录"""
    id: Optional[int] = None
    negotiation_id: str = ""
    offer_id: str = ""
    round_num: int = 0
    perspective: str = ""  # 'recruiter' or 'candidate'
    agent_id: str = ""
    company_offer: str = ""  # JSON string
    candidate_expectation: str = ""  # JSON string
    gap_analysis: str = ""  # JSON string
    proposals: str = ""  # JSON string
    mutual_fit: str = ""  # JSON string
    message_channel: str = ""
    message_body: str = ""
    message_status: str = "pending"  # pending/sent/delivered/read/replied
    deal_reached: bool = False
    sentiment: str = "neutral"
    created_at: Optional[str] = None


class NegotiationHistoryStorage:
    """谈判历史存储"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._ensure_table()

    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self):
        """确保表存在"""
        conn = self._get_connection()
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS negotiation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                negotiation_id TEXT NOT NULL,
                offer_id TEXT NOT NULL,
                round_num INTEGER NOT NULL,
                perspective TEXT NOT NULL,
                agent_id TEXT,
                company_offer TEXT,
                candidate_expectation TEXT,
                gap_analysis TEXT,
                proposals TEXT,
                mutual_fit TEXT,
                message_channel TEXT,
                message_body TEXT,
                message_status TEXT DEFAULT 'pending',
                deal_reached INTEGER DEFAULT 0,
                sentiment TEXT DEFAULT 'neutral',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(negotiation_id, round_num, perspective)
            )
        ''')

        # 创建索引
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_negotiation_id
            ON negotiation_history(negotiation_id)
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_offer_id
            ON negotiation_history(offer_id)
        ''')

        conn.commit()
        conn.close()

    def save_negotiation_round(
        self,
        negotiation_id: str,
        offer_id: str,
        round_num: int,
        perspective: str,
        agent_id: str,
        company_offer: Dict[str, Any],
        candidate_expectation: Dict[str, Any],
        result: Dict[str, Any],
        sentiment: str = "neutral",
    ) -> int:
        """
        保存一轮谈判记录

        Args:
            negotiation_id: 谈判ID
            offer_id: Offer ID
            round_num: 谈判轮次
            perspective: 视角 ('recruiter' or 'candidate')
            agent_id: Agent ID
            company_offer: 公司Offer
            candidate_expectation: 候选人期望
            result: 谈判结果
            sentiment: 情感倾向

        Returns:
            记录的ID
        """
        conn = self._get_connection()
        c = conn.cursor()

        # 提取数据
        gap_analysis = result.get("gap", {})
        proposals = result.get("proposals", [])
        mutual_fit = result.get("mutual_fit", {})
        message = result.get("message", {})
        deal_reached = result.get("deal_reached", False)

        try:
            c.execute('''
                INSERT INTO negotiation_history (
                    negotiation_id, offer_id, round_num, perspective, agent_id,
                    company_offer, candidate_expectation, gap_analysis, proposals,
                    mutual_fit, message_channel, message_body, message_status,
                    deal_reached, sentiment, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                negotiation_id,
                offer_id,
                round_num,
                perspective,
                agent_id,
                json.dumps(company_offer, ensure_ascii=False),
                json.dumps(candidate_expectation, ensure_ascii=False),
                json.dumps(gap_analysis, ensure_ascii=False),
                json.dumps(proposals, ensure_ascii=False),
                json.dumps(mutual_fit, ensure_ascii=False),
                message.get("channel", "wechat"),
                message.get("body", ""),
                message.get("status", "pending"),
                1 if deal_reached else 0,
                sentiment,
                datetime.now().isoformat(),
            ))

            record_id = c.lastrowid
            conn.commit()
        finally:
            conn.close()

        return record_id

    def update_message_status(self, record_id: int, status: str) -> bool:
        """更新消息状态"""
        conn = self._get_connection()
        c = conn.cursor()

        try:
            c.execute('''
                UPDATE negotiation_history
                SET message_status = ?
                WHERE id = ?
            ''', (status, record_id))
            conn.commit()
            return c.rowcount > 0
        finally:
            conn.close()

    def get_negotiation_history(
        self,
        negotiation_id: str,
        perspective: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取谈判历史

        Args:
            negotiation_id: 谈判ID
            perspective: 可选，筛选视角

        Returns:
            谈判记录列表
        """
        conn = self._get_connection()
        c = conn.cursor()

        if perspective:
            c.execute('''
                SELECT * FROM negotiation_history
                WHERE negotiation_id = ? AND perspective = ?
                ORDER BY round_num ASC
            ''', (negotiation_id, perspective))
        else:
            c.execute('''
                SELECT * FROM negotiation_history
                WHERE negotiation_id = ?
                ORDER BY round_num ASC
            ''', (negotiation_id,))

        rows = c.fetchall()
        conn.close()

        return [self._row_to_dict(row) for row in rows]

    def get_offer_negotiation_history(
        self,
        offer_id: str,
    ) -> List[Dict[str, Any]]:
        """获取某个Offer的所有谈判记录"""
        conn = self._get_connection()
        c = conn.cursor()

        c.execute('''
            SELECT * FROM negotiation_history
            WHERE offer_id = ?
            ORDER BY round_num ASC, perspective ASC
        ''', (offer_id,))

        rows = c.fetchall()
        conn.close()

        return [self._row_to_dict(row) for row in rows]

    def get_latest_round(self, negotiation_id: str, perspective: str) -> Optional[Dict[str, Any]]:
        """获取最新一轮谈判记录"""
        conn = self._get_connection()
        c = conn.cursor()

        c.execute('''
            SELECT * FROM negotiation_history
            WHERE negotiation_id = ? AND perspective = ?
            ORDER BY round_num DESC
            LIMIT 1
        ''', (negotiation_id, perspective))

        row = c.fetchone()
        conn.close()

        return self._row_to_dict(row) if row else None

    def is_deal_reached(self, negotiation_id: str) -> bool:
        """检查是否已达成交易"""
        conn = self._get_connection()
        c = conn.cursor()

        c.execute('''
            SELECT deal_reached FROM negotiation_history
            WHERE negotiation_id = ? AND deal_reached = 1
            LIMIT 1
        ''', (negotiation_id,))

        row = c.fetchone()
        conn.close()

        return row is not None

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        if row is None:
            return {}

        result = dict(row)

        # 解析JSON字段
        for field in ['company_offer', 'candidate_expectation', 'gap_analysis',
                       'proposals', 'mutual_fit']:
            if field in result and result[field]:
                try:
                    result[field] = json.loads(result[field])
                except json.JSONDecodeError:
                    pass

        # 转换布尔值
        if 'deal_reached' in result:
            result['deal_reached'] = bool(result['deal_reached'])

        return result


# 全局实例
_storage: Optional[NegotiationHistoryStorage] = None


def get_negotiation_storage() -> NegotiationHistoryStorage:
    """获取全局谈判历史存储实例"""
    global _storage
    if _storage is None:
        _storage = NegotiationHistoryStorage()
    return _storage
