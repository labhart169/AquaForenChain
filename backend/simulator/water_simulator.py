"""Smart-water digital twin and event generator."""
from __future__ import annotations

import random
from collections import Counter
from typing import Dict, List, Tuple

from .scada_events import make_event


EXPERIMENT_TIMESTAMP = "2026-06-08T21:23:35Z"

DEVICE_REGISTRY = [
    {"device_id": "TANK-01", "device_type": "reservoir", "zone": "OT", "location": "North reservoir", "authorized": True},
    {"device_id": "PUMP-01", "device_type": "pump", "zone": "OT", "location": "Pumping station A", "authorized": True},
    {"device_id": "VALVE-01", "device_type": "valve", "zone": "OT", "location": "Distribution valve A", "authorized": True},
    {"device_id": "PRESS-01", "device_type": "pressure_sensor", "zone": "OT", "location": "Main pipe", "authorized": True},
    {"device_id": "FLOW-01", "device_type": "flow_sensor", "zone": "OT", "location": "Main pipe", "authorized": True},
    {"device_id": "CHLOR-01", "device_type": "quality_sensor", "zone": "OT", "location": "Treatment outlet", "authorized": True},
    {"device_id": "GW-01", "device_type": "evidence_gateway", "zone": "EVIDENCE", "location": "SCADA DMZ", "authorized": True},
]


class SmartWaterSimulator:
    """Generate deterministic but realistic enough smart-water events.

    The goal is not hydraulic precision; it is a reproducible cyber-physical
    evidence stream suitable for evaluating integrity, anchoring, verification,
    and reporting workflows.
    """

    def __init__(self, seed: int = 42, fixed_timestamp: str | None = EXPERIMENT_TIMESTAMP) -> None:
        self.rnd = random.Random(seed)
        self.fixed_timestamp = fixed_timestamp
        self.tank_level = 68.0
        self.pressure = 3.4
        self.flow_rate = 120.0
        self.chlorine = 0.72
        self.pump_status = "ON"
        self.valve_status = "OPEN"
        self.network_ok = True

    def _update_state(self) -> None:
        if self.pump_status == "ON" and self.valve_status == "OPEN":
            self.tank_level += self.rnd.uniform(-0.7, 0.4)
            self.pressure += self.rnd.uniform(-0.18, 0.22)
            self.flow_rate += self.rnd.uniform(-6.0, 6.5)
        elif self.pump_status == "OFF":
            self.tank_level += self.rnd.uniform(-1.3, -0.2)
            self.pressure += self.rnd.uniform(-0.35, 0.08)
            self.flow_rate += self.rnd.uniform(-12.0, 2.0)
        else:
            self.pressure += self.rnd.uniform(0.0, 0.45)
            self.flow_rate += self.rnd.uniform(-16.0, -2.0)
        self.chlorine += self.rnd.uniform(-0.03, 0.03)
        self.tank_level = max(5.0, min(98.0, self.tank_level))
        self.pressure = max(0.2, min(8.5, self.pressure))
        self.flow_rate = max(0.0, min(220.0, self.flow_rate))
        self.chlorine = max(0.1, min(1.4, self.chlorine))

    def snapshot(self) -> Dict[str, object]:
        alarms = []
        if self.tank_level < 20:
            alarms.append("LOW_TANK_LEVEL")
        if self.pressure > 6.0:
            alarms.append("HIGH_PRESSURE")
        if self.pressure < 1.5:
            alarms.append("LOW_PRESSURE")
        if self.chlorine < 0.35:
            alarms.append("LOW_CHLORINE")
        status = "ALERT" if alarms else "NORMAL"
        return {
            "tank_level_percent": round(self.tank_level, 3),
            "pressure_bar": round(self.pressure, 3),
            "flow_rate_lpm": round(self.flow_rate, 3),
            "chlorine_mg_l": round(self.chlorine, 3),
            "pump_status": self.pump_status,
            "valve_status": self.valve_status,
            "network_status": "OK" if self.network_ok else "DEGRADED",
            "alarms": ";".join(alarms) if alarms else "NONE",
            "state": status,
        }

    def generate_events(self, count: int = 1000) -> List[Dict[str, object]]:
        events: List[Dict[str, object]] = []
        for idx in range(1, count + 1):
            self._update_state()
            roll = self.rnd.random()
            if roll < 0.20:
                e = make_event(idx=idx, zone="OT", device_id="TANK-01", device_type="reservoir", event_type="TANK_LEVEL_READING", value=round(self.tank_level, 3), unit="%", timestamp=self.fixed_timestamp)
            elif roll < 0.40:
                e = make_event(idx=idx, zone="OT", device_id="PRESS-01", device_type="pressure_sensor", event_type="PRESSURE_READING", value=round(self.pressure, 3), unit="bar", timestamp=self.fixed_timestamp)
            elif roll < 0.58:
                e = make_event(idx=idx, zone="OT", device_id="FLOW-01", device_type="flow_sensor", event_type="FLOW_READING", value=round(self.flow_rate, 3), unit="L/min", timestamp=self.fixed_timestamp)
            elif roll < 0.70:
                e = make_event(idx=idx, zone="OT", device_id="CHLOR-01", device_type="quality_sensor", event_type="CHLORINE_READING", value=round(self.chlorine, 3), unit="mg/L", timestamp=self.fixed_timestamp)
            elif roll < 0.79:
                if self.rnd.random() < 0.18:
                    self.pump_status = "OFF" if self.pump_status == "ON" else "ON"
                e = make_event(idx=idx, zone="OT", device_id="PUMP-01", device_type="pump", event_type="PUMP_STATE_CHANGE", value=self.pump_status, operator_id="OP-01", timestamp=self.fixed_timestamp)
            elif roll < 0.87:
                if self.rnd.random() < 0.14:
                    self.valve_status = "CLOSED" if self.valve_status == "OPEN" else "OPEN"
                e = make_event(idx=idx, zone="OT", device_id="VALVE-01", device_type="valve", event_type="VALVE_STATE_CHANGE", value=self.valve_status, operator_id="OP-02", timestamp=self.fixed_timestamp)
            elif roll < 0.93:
                alarm = "HIGH_PRESSURE" if self.pressure > 5.2 else "ANOMALY_CHECK_REQUIRED"
                e = make_event(idx=idx, zone="OT", device_id="SCADA-01", device_type="scada_server", event_type="ALARM_RAISED", value=alarm, operator_id="AUTO", description="SCADA alarm generated by threshold logic", timestamp=self.fixed_timestamp)
            elif roll < 0.97:
                action = self.rnd.choice(["ACK_ALARM", "CHANGE_THRESHOLD", "START_PUMP", "OPEN_VALVE"])
                e = make_event(idx=idx, zone="OT", device_id="HMI-01", device_type="hmi", event_type="OPERATOR_ACTION", value=action, operator_id=self.rnd.choice(["OP-01", "OP-02", "SUP-01"]), source="HMI", timestamp=self.fixed_timestamp)
            elif roll < 0.99:
                self.network_ok = not self.network_ok if self.rnd.random() < 0.5 else self.network_ok
                e = make_event(idx=idx, zone="OT", device_id="GW-01", device_type="gateway", event_type="NETWORK_STATUS", value="OK" if self.network_ok else "DEGRADED", source="Gateway", timestamp=self.fixed_timestamp)
            else:
                e = make_event(idx=idx, zone="OT", device_id="IDS-01", device_type="ids", event_type="SECURITY_EVENT", value="SUSPICIOUS_SEQUENCE", source="IDS", description="Suspicious state transition observed", timestamp=self.fixed_timestamp)
            events.append(e)
        return events


def summarize_events(events: List[Dict[str, object]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    return dict(Counter(e["event_type"] for e in events)), dict(Counter(e["severity"] for e in events))
