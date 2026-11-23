"""Persistence repository for events, evidence batches and custody trails."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .database import connect, init_db


def save_all(db_path: str | Path, events: List[Dict[str, object]], evidence_bundle: Dict[str, object], custody_trail: List[Dict[str, object]]) -> None:
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM evidence")
        conn.execute("DELETE FROM batches")
        conn.execute("DELETE FROM custody")
        for e in events:
            conn.execute(
                "INSERT OR REPLACE INTO events(event_id,timestamp,device_id,device_type,event_type,value,unit,severity,source,raw_json) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (e["event_id"], e["timestamp"], e["device_id"], e["device_type"], e["event_type"], str(e["value"]), e.get("unit", ""), e["severity"], e["source"], json.dumps(e, ensure_ascii=False)),
            )
        conn.execute(
            "INSERT OR REPLACE INTO batches(batch_id,evidence_count,merkle_root,merkle_depth,raw_json) VALUES(?,?,?,?,?)",
            (evidence_bundle["batch_id"], evidence_bundle["evidence_count"], evidence_bundle["merkle_root"], evidence_bundle["merkle_depth"], json.dumps(evidence_bundle, ensure_ascii=False)),
        )
        for row in evidence_bundle["evidence"]:
            conn.execute(
                "INSERT OR REPLACE INTO evidence(evidence_id,event_id,batch_id,event_hash,merkle_root,verified,raw_json) VALUES(?,?,?,?,?,?,?)",
                (row["evidence_id"], row["event_id"], row["batch_id"], row["event_hash"], row["merkle_root"], int(bool(row.get("verified"))), json.dumps(row, ensure_ascii=False)),
            )
        for row in custody_trail:
            conn.execute(
                "INSERT OR REPLACE INTO custody(custody_id,evidence_id,actor,action,previous_hash,custody_hash,raw_json) VALUES(?,?,?,?,?,?,?)",
                (row["custody_id"], row["evidence_id"], row["actor"], row["action"], row["previous_hash"], row["custody_hash"], json.dumps(row, ensure_ascii=False)),
            )
        conn.commit()


def fetch_counts(db_path: str | Path = "data/events.db") -> Dict[str, int]:
    init_db(db_path)
    with connect(db_path) as conn:
        return {
            "events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            "evidence": conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
            "batches": conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0],
            "custody": conn.execute("SELECT COUNT(*) FROM custody").fetchone()[0],
        }
