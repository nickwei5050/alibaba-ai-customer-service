"""SQLite-backed dedupe store for processed inquiry emails."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ProcessedStore:
    """Tracks which emails we have already handled, keyed by dedupe key."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_emails (
                dedupe_key TEXT PRIMARY KEY,
                subject    TEXT,
                buyer_name TEXT,
                url        TEXT,
                processed_at TEXT
            )
            """
        )
        self._conn.commit()

    def seen(self, key: str) -> bool:
        cur = self._conn.execute(
            "SELECT 1 FROM processed_emails WHERE dedupe_key = ?", (key,)
        )
        return cur.fetchone() is not None

    def mark(self, key: str, *, subject: str = "", buyer_name: str = "", url: str = "") -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO processed_emails "
            "(dedupe_key, subject, buyer_name, url, processed_at) VALUES (?, ?, ?, ?, ?)",
            (key, subject, buyer_name, url, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
