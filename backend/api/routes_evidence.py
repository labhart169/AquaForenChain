from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:
    APIRouter = None
from backend.evidence.verifier import verify_event_against_root

router = APIRouter(prefix="/evidence", tags=["evidence"]) if APIRouter else None

if router:
    @router.post("/verify")
    def verify(payload: dict):
        return verify_event_against_root(payload["event"], payload["proof"], payload["merkle_root"])
