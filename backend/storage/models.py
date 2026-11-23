"""Lightweight data model constants for SQLite persistence."""
EVENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    timestamp TEXT,
    device_id TEXT,
    device_type TEXT,
    event_type TEXT,
    value TEXT,
    unit TEXT,
    severity TEXT,
    source TEXT,
    raw_json TEXT NOT NULL
)
"""

EVIDENCE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    event_id TEXT,
    batch_id TEXT,
    event_hash TEXT,
    merkle_root TEXT,
    verified INTEGER DEFAULT 0,
    raw_json TEXT NOT NULL
)
"""

BATCH_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS batches (
    batch_id TEXT PRIMARY KEY,
    evidence_count INTEGER,
    merkle_root TEXT,
    merkle_depth INTEGER,
    raw_json TEXT NOT NULL
)
"""

CUSTODY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS custody (
    custody_id TEXT PRIMARY KEY,
    evidence_id TEXT,
    actor TEXT,
    action TEXT,
    previous_hash TEXT,
    custody_hash TEXT,
    raw_json TEXT NOT NULL
)
"""
