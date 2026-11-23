from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:
    APIRouter = None
from backend.blockchain.web3_client import Web3Client

router = APIRouter(prefix="/blockchain", tags=["blockchain"]) if APIRouter else None

if router:
    @router.get("/status")
    def status():
        return Web3Client().status().__dict__
