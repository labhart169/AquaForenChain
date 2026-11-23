"""Evidence verification helpers."""
from __future__ import annotations

from typing import Dict, List, Any

from .hashing import sha256_hex
from .merkle import verify_proof


def verify_event_against_root(event: Dict[str, object], proof: List[Dict[str, str]], merkle_root: str) -> Dict[str, object]:
    h = sha256_hex(event)
    ok = verify_proof(h, proof, merkle_root)
    return {"event_hash": h, "merkle_root": merkle_root, "valid": ok, "status": "VALID" if ok else "TAMPERED_OR_MISSING"}


def verify_device_authorized(event: Dict[str, object], device_registry: List[Dict[str, object]]) -> bool:
    authorized = {d["device_id"] for d in device_registry if d.get("authorized") is True}
    return event.get("device_id") in authorized


def verify_custody_trail(trail: List[Dict[str, object]]) -> Dict[str, object]:
    from .hashing import sha256_hex
    previous = "GENESIS"
    for row in trail:
        if row.get("previous_hash") != previous:
            return {"valid": False, "broken_at": row.get("custody_id"), "reason": "previous_hash_mismatch"}
        cloned = dict(row)
        custody_hash = cloned.pop("custody_hash", None)
        if sha256_hex(cloned) != custody_hash:
            return {"valid": False, "broken_at": row.get("custody_id"), "reason": "custody_hash_mismatch"}
        previous = custody_hash
    return {"valid": True, "actions": len(trail)}


def verify_batch_inventory(events: List[Dict[str, Any]], bundle: Dict[str, Any]) -> Dict[str, object]:
    """Verify that an ordered event collection matches the committed batch inventory.

    The check is intentionally independent from Merkle-proof verification: it detects
    missing, extra, or reordered events by comparing the expected count and ordered
    canonical SHA-256 digest list archived in the evidence bundle.
    """
    expected_count = int(bundle.get("evidence_count", 0))
    if len(events) != expected_count:
        return {
            "valid": False,
            "reason": "evidence_count_mismatch",
            "expected_count": expected_count,
            "actual_count": len(events),
        }

    expected_hashes = list(bundle.get("event_hashes", []))
    actual_hashes = [sha256_hex(e) for e in events]
    if len(expected_hashes) != expected_count:
        return {
            "valid": False,
            "reason": "bundle_inventory_length_mismatch",
            "expected_count": expected_count,
            "inventory_hashes": len(expected_hashes),
        }

    for i, (expected, actual) in enumerate(zip(expected_hashes, actual_hashes)):
        if expected != actual:
            return {
                "valid": False,
                "reason": "ordered_inventory_hash_mismatch",
                "index": i,
                "expected_hash": expected,
                "actual_hash": actual,
            }
    return {"valid": True, "evidence_count": expected_count}


def detect_replay_candidate(candidate: Dict[str, Any], known_events: List[Dict[str, Any]]) -> Dict[str, object]:
    """Detect a replay candidate using identifiers that should be unique in a batch.

    The simulator's replay mutation intentionally preserves the original nonce while
    assigning a new event_id/sequence. A duplicate nonce therefore provides a concrete
    deterministic replay-consistency failure without claiming network IDS accuracy.
    """
    nonce = candidate.get("nonce")
    event_id = candidate.get("event_id")
    duplicate_nonce = nonce is not None and any(e.get("nonce") == nonce for e in known_events)
    duplicate_event_id = event_id is not None and any(e.get("event_id") == event_id for e in known_events)
    detected = bool(duplicate_nonce or duplicate_event_id)
    return {
        "detected": detected,
        "duplicate_nonce": duplicate_nonce,
        "duplicate_event_id": duplicate_event_id,
    }
