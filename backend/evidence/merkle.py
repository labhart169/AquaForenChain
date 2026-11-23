"""Merkle tree generation and verification."""
from __future__ import annotations

from typing import List, Dict, Tuple

from .hashing import sha256_hex


def _norm(h: str) -> str:
    return h[2:] if h.startswith("0x") else h


def hash_pair(left: str, right: str) -> str:
    return sha256_hex(_norm(left) + _norm(right))


class MerkleTree:
    def __init__(self, leaves: List[str]) -> None:
        if not leaves:
            leaves = [sha256_hex("")]
        self.leaves = [_norm(x) for x in leaves]
        self.levels: List[List[str]] = [self.leaves]
        current = self.leaves
        while len(current) > 1:
            nxt = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                nxt.append(hash_pair(left, right))
            self.levels.append(nxt)
            current = nxt

    @property
    def root(self) -> str:
        return self.levels[-1][0]

    @property
    def depth(self) -> int:
        return len(self.levels) - 1

    def proof(self, index: int) -> List[Dict[str, str]]:
        proof: List[Dict[str, str]] = []
        idx = index
        for level in self.levels[:-1]:
            sibling_idx = idx ^ 1
            if sibling_idx >= len(level):
                sibling_idx = idx
            side = "right" if idx % 2 == 0 else "left"
            proof.append({"side": side, "hash": level[sibling_idx]})
            idx //= 2
        return proof


def verify_proof(leaf_hash: str, proof: List[Dict[str, str]], root: str) -> bool:
    acc = _norm(leaf_hash)
    for item in proof:
        sibling = _norm(item["hash"])
        if item["side"] == "right":
            acc = hash_pair(acc, sibling)
        else:
            acc = hash_pair(sibling, acc)
    return acc == _norm(root)
