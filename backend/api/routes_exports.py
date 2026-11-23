from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:
    APIRouter = None
from pathlib import Path

router = APIRouter(prefix="/exports", tags=["exports"]) if APIRouter else None

if router:
    @router.get("/files")
    def files():
        base = Path("results")
        return [str(p) for p in base.rglob("*") if p.is_file()]
