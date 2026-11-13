import sqlite3
from config import DB_PATH, TREND_IDS
from models import Reading


class Storage:
    """SQLite (WAL-режим). Хранит валидные значения + тренды + невалидные (доп. таблица)."""

    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            source_id INTEGER NOT NULL,
            object_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            value TEXT NOT NULL,
            is_trend INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_readings_ts ON readings(ts);
        CREATE INDEX IF NOT EXISTS idx_readings_obj ON readings(object_id);

        CREATE TABLE IF NOT EXISTS trend_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            source_id INTEGER NOT NULL,
            object_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            value TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_trend_ts ON trend_journal(ts);

        CREATE TABLE IF NOT EXISTS invalid_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            source_id INTEGER NOT NULL,
            object_id TEXT,
            kind TEXT,
            raw TEXT,
            reason TEXT
        );
        """)
        self.conn.commit()

    def save_reading(self, r: Reading) -> None:
        self.conn.execute(
            "INSERT INTO readings(ts, source_id, object_id, kind, value, is_trend) VALUES (?,?,?,?,?,?)",
            (r.ts, r.source_id, r.object_id, r.kind, repr(r.value), int(r.object_id in TREND_IDS)),
        )

    def save_trend(self, r: Reading) -> None:
        self.conn.execute(
            "INSERT INTO trend_journal(ts, source_id, object_id, kind, value) VALUES (?,?,?,?,?)",
            (r.ts, r.source_id, r.object_id, r.kind, repr(r.value)),
        )

    def log_invalid(self, r: Reading, reason: str) -> None:
        self.conn.execute(
            "INSERT INTO invalid_log(ts, source_id, object_id, kind, raw, reason) VALUES (?,?,?,?,?,?)",
            (r.ts, r.source_id, r.object_id, r.kind, repr(r.value), reason),
        )

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()