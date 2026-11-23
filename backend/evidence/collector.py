"""Evidence collection, batching, and custody generation."""
from __future__ import annotations

from typing import Dict, List

from .hashing import sha256_hex
from .merkle import MerkleTree


def build_evidence(events: List[Dict[str, object]], batch_id: str = "BATCH-000001") -> Dict[str, object]:
    evidence_rows: List[Dict[str, object]] = []
    event_hashes: List[str] = []
    for i, event in enumerate(events):
        event_hash = sha256_hex(event)
        event_hashes.append(event_hash)
        evidence_rows.append({
            "evidence_id": f"EVD-{i+1:06d}",
            "event_id": event["event_id"],
            "device_id": event["device_id"],
            "event_type": event["event_type"],
            "severity": event["severity"],
            "event_hash": event_hash,
            "batch_id": batch_id,
            "anchored": False,
            "verified": False,
        })
    tree = MerkleTree(event_hashes)
    for i, row in enumerate(evidence_rows):
        row["merkle_root"] = tree.root
        row["merkle_depth"] = tree.depth
        row["proof_length"] = len(tree.proof(i))
    return {
        "batch_id": batch_id,
        "evidence_count": len(events),
        "event_hashes": event_hashes,
        "merkle_root": tree.root,
        "merkle_depth": tree.depth,
        "evidence": evidence_rows,
        "proofs": {row["evidence_id"]: tree.proof(i) for i, row in enumerate(evidence_rows)},
    }


def make_custody_trail(evidence_rows: List[Dict[str, object]], analysts: List[str] | None = None) -> List[Dict[str, object]]:
    analysts = analysts or ["ANALYST-01", "AUDITOR-01", "SUPERVISOR-01"]
    trail = []
    previous = "GENESIS"
    actions = ["CREATE_CASE", "VIEW_EVIDENCE", "VERIFY_HASH", "EXPORT_REPORT"]
    max_items = min(72, max(1, len(evidence_rows)))
    for i in range(max_items):
        ev = evidence_rows[i % len(evidence_rows)] if evidence_rows else {"evidence_id": "EVD-000000"}
        row = {
            "custody_id": f"CUST-{i+1:06d}",
            "evidence_id": ev["evidence_id"],
            "actor": analysts[i % len(analysts)],
            "action": actions[i % len(actions)],
            "previous_hash": previous,
        }
        row["custody_hash"] = sha256_hex(row)
        previous = row["custody_hash"]
        trail.append(row)
    return trail
