"""Persist every inquiry to SQLite — the source of truth for the CRM."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..entity.models import InquiryRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    platform TEXT,
    buyer_name TEXT,
    country TEXT,
    product_title TEXT,
    product_url TEXT,
    buyer_message TEXT,
    ai_intent TEXT,
    customer_level TEXT,
    missing_info TEXT,
    ai_reply_en TEXT,
    ai_reply_cn TEXT,
    auto_send INTEGER,
    approval_required INTEGER,
    status TEXT,
    screenshot_path TEXT,
    next_follow_up_time TEXT,
    email_message_id TEXT,
    chat_history TEXT,
    debug_report_path TEXT
)
"""

# Columns added after the first release; ensured on existing DBs at startup.
_MIGRATIONS = (
    ("missing_info", "TEXT"),
    ("ai_reply_cn", "TEXT"),
    ("email_message_id", "TEXT"),
    ("chat_history", "TEXT"),
    ("debug_report_path", "TEXT"),
)


class SqliteLogger:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(_SCHEMA)
        self._migrate()
        self._conn.commit()

    def _migrate(self) -> None:
        existing = {row[1] for row in self._conn.execute("PRAGMA table_info(inquiries)")}
        for col, decl in _MIGRATIONS:
            if col not in existing:
                self._conn.execute(f"ALTER TABLE inquiries ADD COLUMN {col} {decl}")

    def log(self, record: InquiryRecord) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO inquiries (
                date, platform, buyer_name, country, product_title, product_url,
                buyer_message, ai_intent, customer_level, missing_info, ai_reply_en,
                ai_reply_cn, auto_send, approval_required, status, screenshot_path,
                next_follow_up_time, email_message_id, chat_history, debug_report_path
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                record.date.isoformat(),
                record.platform,
                record.buyer_name,
                record.country,
                record.product_title,
                record.product_url,
                record.buyer_message,
                record.ai_intent,
                record.customer_level,
                record.missing_info,
                record.ai_reply_en,
                record.ai_reply_cn,
                int(record.auto_send),
                int(record.approval_required),
                record.status,
                record.screenshot_path,
                record.next_follow_up_time.isoformat() if record.next_follow_up_time else None,
                record.email_message_id,
                record.chat_history,
                record.debug_report_path,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def close(self) -> None:
        self._conn.close()
