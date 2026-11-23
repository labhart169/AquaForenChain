from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:
    APIRouter = None
from backend.storage.repository import fetch_counts

router = APIRouter(prefix="/dashboard", tags=["dashboard"]) if APIRouter else None

if router:
    @router.get("/summary")
    def summary():
        return fetch_counts("data/events.db")
