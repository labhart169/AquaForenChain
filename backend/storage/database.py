"""SQLite connection and initialization."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import EVENTS_TABLE_SQL, EVIDENCE_TABLE_SQL, BATCH_TABLE_SQL, CUSTODY_TABLE_SQL


def connect(db_path: str | Path = "data/events.db") -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = "data/events.db") -> None:
    with connect(db_path) as conn:
        conn.execute(EVENTS_TABLE_SQL)
        conn.execute(EVIDENCE_TABLE_SQL)
        conn.execute(BATCH_TABLE_SQL)
        conn.execute(CUSTODY_TABLE_SQL)
        conn.commit()
