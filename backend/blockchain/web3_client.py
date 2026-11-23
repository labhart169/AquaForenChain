"""Optional Web3 client. The prototype remains usable without a running chain."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Web3Status:
    available: bool
    connected: bool
    message: str
    chain_id: Optional[int] = None


class Web3Client:
    def __init__(self, rpc_url: str = "http://127.0.0.1:8545") -> None:
        self.rpc_url = rpc_url
        self.w3 = None
        try:
            from web3 import Web3
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        except Exception:
            self.w3 = None

    def status(self) -> Web3Status:
        if self.w3 is None:
            return Web3Status(False, False, "web3 package is not installed")
        try:
            connected = self.w3.is_connected()
            chain_id = self.w3.eth.chain_id if connected else None
            return Web3Status(True, connected, "connected" if connected else "not connected", chain_id)
        except Exception as exc:
            return Web3Status(True, False, str(exc))
