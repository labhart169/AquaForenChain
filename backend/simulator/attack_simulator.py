"""Defensive incident simulations used to verify evidence integrity."""
from __future__ import annotations

import copy
from typing import Dict, List, Tuple


def tamper_event(event: Dict[str, object]) -> Dict[str, object]:
    changed = copy.deepcopy(event)
    changed["value"] = "TAMPERED_VALUE"
    changed["description"] = "Tampered locally after anchoring"
    return changed


def delete_event(events: List[Dict[str, object]], index: int = 0) -> List[Dict[str, object]]:
    altered = list(copy.deepcopy(events))
    if altered:
        altered.pop(max(0, min(index, len(altered) - 1)))
    return altered


def replay_event(event: Dict[str, object], new_sequence: int) -> Dict[str, object]:
    replayed = copy.deepcopy(event)
    replayed["sequence"] = new_sequence
    replayed["event_id"] = f"EVT-REPLAY-{new_sequence:06d}"
    replayed["description"] = "Replayed old event under a new sequence"
    return replayed


def manipulate_timestamp(event: Dict[str, object]) -> Dict[str, object]:
    altered = copy.deepcopy(event)
    altered["timestamp"] = "2000-01-01T00:00:00Z"
    altered["description"] = "Timestamp manipulated after original event creation"
    return altered


def unauthorized_device_event(index: int = 999999) -> Dict[str, object]:
    return {
        "event_id": f"EVT-UNAUTH-{index}",
        "timestamp": "2026-06-08T00:00:00Z",
        "zone": "OT",
        "device_id": "FAKE-SENSOR-99",
        "device_type": "unknown_sensor",
        "event_type": "PRESSURE_READING",
        "value": 0.1,
        "unit": "bar",
        "severity": "CRITICAL",
        "operator_id": "UNKNOWN",
        "source": "Unknown",
        "sequence": index,
        "nonce": f"FAKE-{index}",
        "location": "Unknown",
        "description": "Unauthorized device event injected into the evidence pipeline",
    }


def default_attack_scenarios(events: List[Dict[str, object]]) -> List[Dict[str, object]]:
    reference = events[min(5, len(events) - 1)] if events else unauthorized_device_event()
    return [
        {"scenario": "Log tampering", "altered_event": tamper_event(reference), "expected": "DETECTED"},
        {"scenario": "Evidence deletion", "altered_events_count": max(0, len(events) - 1), "expected": "DETECTED"},
        {"scenario": "Replay event", "altered_event": replay_event(reference, 888888), "expected": "DETECTED"},
        {"scenario": "Timestamp manipulation", "altered_event": manipulate_timestamp(reference), "expected": "DETECTED"},
        {"scenario": "Unauthorized device", "altered_event": unauthorized_device_event(), "expected": "DETECTED"},
        {"scenario": "Custody-trail alteration", "altered_custody_hash": "0xdeadbeef", "expected": "DETECTED"},
    ]
