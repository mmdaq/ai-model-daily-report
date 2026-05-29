import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from collectors.base import ModelRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    author TEXT,
    source_platform TEXT NOT NULL,
    model_type TEXT,
    model_size TEXT,
    is_gguf INTEGER DEFAULT 0,
    quant_method TEXT,
    vae TEXT,
    clip TEXT,
    workflow TEXT,
    download_url TEXT,
    description TEXT,
    dedup_key TEXT UNIQUE NOT NULL,
    first_seen_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS report_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT UNIQUE NOT NULL,
    sent_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def insert_model(self, record: ModelRecord) -> bool:
        """Insert model if new. Returns True if inserted."""
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO models (
                        model_name, author, source_platform, model_type,
                        model_size, is_gguf, quant_method, vae, clip,
                        workflow, download_url, description, dedup_key,
                        first_seen_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.model_name,
                        record.author,
                        record.source_platform,
                        record.model_type,
                        record.model_size,
                        record.is_gguf,
                        record.quant_method,
                        record.vae,
                        record.clip,
                        record.workflow,
                        record.download_url,
                        record.description,
                        record.dedup_key(),
                        now,
                        now,
                    ),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def get_today_models(self, target_date: Optional[date] = None) -> list[dict]:
        target = target_date or date.today()
        prefix = target.isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM models
                WHERE first_seen_at LIKE ?
                ORDER BY first_seen_at DESC
                """,
                (f"{prefix}%",),
            ).fetchall()
        return [dict(row) for row in rows]

    def has_report_sent_today(self, target_date: Optional[date] = None) -> bool:
        target = (target_date or date.today()).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM report_log WHERE report_date = ?", (target,)
            ).fetchone()
        return row is not None

    def mark_report_sent(self, target_date: Optional[date] = None) -> None:
        target = (target_date or date.today()).isoformat()
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO report_log (report_date, sent_at)
                VALUES (?, ?)
                """,
                (target, now),
            )
