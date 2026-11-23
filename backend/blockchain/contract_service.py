"""Build blockchain payloads and optionally anchor them."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Any

from .web3_client import Web3Client


def build_anchor_payload(batch_id: str, merkle_root: str, evidence_count: int, offchain_hash: str) -> Dict[str, Any]:
    return {
        "batch_id": batch_id,
        "merkle_root": "0x" + merkle_root.replace("0x", ""),
        "evidence_count": int(evidence_count),
        "offchain_hash": "0x" + offchain_hash.replace("0x", ""),
    }


def write_payload(path: str | Path, payload: Dict[str, Any]) -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def anchor_batch_if_possible(payload: Dict[str, Any], contract_address: str | None = None, abi_path: str | Path | None = None) -> Dict[str, Any]:
    """Return a receipt-like dictionary.

    To keep the code safe and portable, actual Ethereum submission requires a
    deployed contract address and ABI. Otherwise the function returns a clear
    NOT_ANCHORED status instead of inventing gas or transaction hashes.
    """
    started = time.perf_counter()
    client = Web3Client()
    status = client.status()
    if not status.connected or not contract_address or not abi_path:
        return {
            "anchored": False,
            "status": "NOT_ANCHORED_RUN_HARDHAT_AND_DEPLOY_CONTRACT",
            "rpc_status": status.__dict__,
            "batch_id": payload.get("batch_id"),
            "gas_used": None,
            "block_number": None,
            "transaction_hash": None,
            "anchoring_latency_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    # Production anchoring can be added here once contract ABI/address are present.
    return {
        "anchored": False,
        "status": "ABI_ADDRESS_PROVIDED_BUT_PYTHON_SUBMISSION_NOT_ENABLED_USE_NPM_RUN_ANCHOR",
        "batch_id": payload.get("batch_id"),
        "gas_used": None,
        "block_number": None,
        "transaction_hash": None,
        "anchoring_latency_ms": round((time.perf_counter() - started) * 1000, 3),
    }
