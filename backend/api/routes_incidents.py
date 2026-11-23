from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:
    APIRouter = None
from backend.simulator.attack_simulator import default_attack_scenarios

router = APIRouter(prefix="/incidents", tags=["incidents"]) if APIRouter else None

if router:
    @router.get("/scenarios")
    def scenarios():
        return default_attack_scenarios([])
