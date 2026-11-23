from __future__ import annotations

import argparse
import copy
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Any

from backend.simulator.water_simulator import SmartWaterSimulator, DEVICE_REGISTRY, summarize_events
from backend.simulator.attack_simulator import default_attack_scenarios, tamper_event, delete_event, manipulate_timestamp, replay_event, unauthorized_device_event
from backend.evidence.collector import build_evidence, make_custody_trail
from backend.evidence.hashing import sha256_hex, canonical_json
from backend.evidence.merkle import MerkleTree
from backend.evidence.verifier import verify_event_against_root, verify_device_authorized, verify_custody_trail, verify_batch_inventory, detect_replay_candidate
from backend.storage.repository import save_all
from backend.exports.export_csv import write_csv
from backend.exports.export_excel import write_excel
from backend.exports.export_latex import write_latex_table
from backend.exports.export_figures import write_simple_svg_bar
from backend.exports.export_pdf import write_report
from backend.blockchain.contract_service import build_anchor_payload, write_payload, anchor_batch_if_possible

try:
    from fastapi import FastAPI
    from backend.api.routes_dashboard import router as dashboard_router
    from backend.api.routes_evidence import router as evidence_router
    from backend.api.routes_blockchain import router as blockchain_router
    from backend.api.routes_incidents import router as incidents_router
    from backend.api.routes_exports import router as exports_router
except Exception:
    FastAPI = None

if FastAPI:
    app = FastAPI(title="AquaForenChain API", version="1.0.0")
    for r in [dashboard_router, evidence_router, blockchain_router, incidents_router, exports_router]:
        if r:
            app.include_router(r)
else:
    app = None


def ensure_output_dirs(base: Path) -> None:
    for sub in ["csv", "excel", "latex", "figures", "reports", "raw", "json", "blockchain/payloads", "blockchain/receipts"]:
        (base / sub).mkdir(parents=True, exist_ok=True)
    for sub in ["data/raw_events", "data/evidence_store"]:
        Path(sub).mkdir(parents=True, exist_ok=True)


def rows_from_counter(counter: Dict[str, int], key_name: str) -> List[Dict[str, Any]]:
    return [{key_name: k, "count": v} for k, v in sorted(counter.items())]


def architecture_zones() -> List[Dict[str, str]]:
    return [
        {"zone": "OT smart-water zone", "components": "reservoir, pump, valve, pressure/flow/chlorine sensors, HMI/SCADA", "trust_assumption": "operational but potentially compromised", "output": "raw operational and security events"},
        {"zone": "Evidence-processing zone", "components": "collector, canonicalizer, SHA-256 hashing, Merkle batching", "trust_assumption": "hardened gateway/DMZ service", "output": "hashes, proofs, Merkle roots"},
        {"zone": "Ledger-commitment zone", "components": "Ethereum, EvidenceAnchor, DeviceRegistry, ChainOfCustody", "trust_assumption": "tamper-evident commitment layer", "output": "immutable batch commitments"},
        {"zone": "Investigation/reporting zone", "components": "dashboard, verifier, result generator", "trust_assumption": "analyst-facing forensic workspace", "output": "CSV, Excel, LaTeX, figures, reports"},
    ]


def requirements_traceability() -> List[Dict[str, str]]:
    return [
        {"requirement": "Evidence integrity", "mechanism": "canonical SHA-256 hash + Merkle proof", "validation": "tampered event invalidates root verification"},
        {"requirement": "Selective anchoring", "mechanism": "one Merkle root per batch", "validation": "commitment and transaction reduction ratios"},
        {"requirement": "Device accountability", "mechanism": "DeviceRegistry smart contract + local registry", "validation": "unauthorized device scenario rejected"},
        {"requirement": "Forensic traceability", "mechanism": "hash-linked chain of custody", "validation": "custody alteration scenario detected"},
        {"requirement": "Article-ready reproducibility", "mechanism": "deterministic seed + automatic exports", "validation": "CSV/JSON/LaTeX/SVG files generated"},
    ]


def threat_model_matrix() -> List[Dict[str, str]]:
    return [
        {"threat": "Log tampering", "attacker_capability": "modify off-chain event value", "expected_detection": "hash and Merkle proof mismatch"},
        {"threat": "Evidence deletion", "attacker_capability": "remove stored evidence", "expected_detection": "missing evidence from anchored batch"},
        {"threat": "Replay event", "attacker_capability": "reuse old valid event", "expected_detection": "event_id/nonce/sequence inconsistency"},
        {"threat": "Timestamp manipulation", "attacker_capability": "alter time field", "expected_detection": "canonical hash mismatch"},
        {"threat": "Unauthorized device", "attacker_capability": "inject fake sensor event", "expected_detection": "device registry rejection"},
        {"threat": "Custody alteration", "attacker_capability": "change analyst action record", "expected_detection": "hash-linked custody break"},
    ]


def evaluate_scalability(events: List[Dict[str, Any]], batch_sizes: List[int]) -> List[Dict[str, Any]]:
    rows = []
    for size in batch_sizes:
        subset = events[:min(size, len(events))]
        hashes = [sha256_hex(e) for e in subset]
        t0 = time.perf_counter()
        tree = MerkleTree(hashes)
        merkle_ms = (time.perf_counter() - t0) * 1000
        idx = min(3, len(subset)-1) if subset else 0
        proof = tree.proof(idx)
        t1 = time.perf_counter()
        valid = verify_event_against_root(subset[idx], proof, tree.root)["valid"] if subset else True
        verify_ms = (time.perf_counter() - t1) * 1000
        rows.append({
            "batch_size": len(subset),
            "merkle_depth": tree.depth,
            "proof_length": len(proof),
            "merkle_generation_ms": round(merkle_ms, 4),
            "verification_ms": round(verify_ms, 4),
            "verification_valid": valid,
            "direct_commitments": len(subset),
            "merkle_commitments": 1,
            "commitment_reduction_ratio": round(len(subset) / 1, 2) if subset else 0,
            "transaction_reduction_ratio": round(len(subset) / 1, 2) if subset else 0,
            "onchain_bytes_direct_sha256": len(subset) * 32,
            "onchain_bytes_merkle_root": 32,
        })
    return rows


def evaluate_attacks(events: List[Dict[str, Any]], bundle: Dict[str, Any], custody: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute six deterministic post-capture integrity consistency tests.

    These are mechanism tests, not an intrusion-detection benchmark. Every ``detected``
    value is produced by an actual verifier/inventory/device/custody check; no scenario
    is hard-coded to pass.
    """
    ref_idx = min(5, len(events) - 1)
    ref_event = events[ref_idx]
    ref_evd = bundle["evidence"][ref_idx]
    proof = bundle["proofs"][ref_evd["evidence_id"]]
    root = bundle["merkle_root"]

    tampered = tamper_event(ref_event)
    deleted_events = delete_event(events, ref_idx)
    replay = replay_event(ref_event, 777777)
    timestamp = manipulate_timestamp(ref_event)
    unauth = unauthorized_device_event()

    altered_custody = copy.deepcopy(custody)
    if altered_custody:
        altered_custody[min(2, len(altered_custody) - 1)]["action"] = "TAMPERED_CUSTODY_ACTION"

    deletion_check = verify_batch_inventory(deleted_events, bundle)
    replay_check = detect_replay_candidate(replay, events)
    custody_check = verify_custody_trail(altered_custody)

    rows = [
        {"scenario": "Log tampering", "expected": "DETECTED", "detected": not verify_event_against_root(tampered, proof, root)["valid"], "mechanism": "canonical hash + Merkle proof mismatch"},
        {"scenario": "Evidence deletion", "expected": "DETECTED", "detected": not deletion_check["valid"], "mechanism": f"ordered batch inventory ({deletion_check.get('reason', 'valid')})"},
        {"scenario": "Replay event", "expected": "DETECTED", "detected": replay_check["detected"], "mechanism": "duplicate event identifier/nonce consistency check"},
        {"scenario": "Timestamp manipulation", "expected": "DETECTED", "detected": not verify_event_against_root(timestamp, proof, root)["valid"], "mechanism": "canonical hash + Merkle proof mismatch"},
        {"scenario": "Unauthorized device", "expected": "DETECTED", "detected": not verify_device_authorized(unauth, DEVICE_REGISTRY), "mechanism": "authorized-device registry check"},
        {"scenario": "Custody-trail alteration", "expected": "DETECTED", "detected": not custody_check["valid"], "mechanism": f"hash-linked custody verification ({custody_check.get('reason', 'valid')})"},
    ]
    for row in rows:
        row["result"] = "PASS" if row["detected"] else "FAIL"
    return rows


def run_experiment(events_count: int, batch_sizes: List[int], seed: int, output_dir: str, anchor_on_chain: bool = False) -> Dict[str, Any]:
    base = Path(output_dir)
    ensure_output_dirs(base)
    sim = SmartWaterSimulator(seed=seed)
    events = sim.generate_events(events_count)
    twin_snapshot = sim.snapshot()
    bundle = build_evidence(events, batch_id="BATCH-FINAL-000001")
    custody = make_custody_trail(bundle["evidence"])
    save_all("data/events.db", events, bundle, custody)

    event_dist, severity_dist = summarize_events(events)
    scalability = evaluate_scalability(events, batch_sizes)
    attacks = evaluate_attacks(events, bundle, custody)
    custody_check = verify_custody_trail(custody)

    # Commit the exact canonical evidence-bundle representation. The canonical sidecar
    # written below hashes byte-for-byte to ``offchain_hash``.
    canonical_bundle = canonical_json(bundle)
    offchain_hash = sha256_hex(canonical_bundle.encode("utf-8"))
    payload = build_anchor_payload(bundle["batch_id"], bundle["merkle_root"], bundle["evidence_count"], offchain_hash)
    write_payload(base / "blockchain/payloads/anchor_payload.json", payload)
    receipt = anchor_batch_if_possible(payload) if anchor_on_chain else {"anchored": False, "status": "NOT_REQUESTED_USE_HARDHAT_FOR_REAL_GAS", "batch_id": bundle["batch_id"], "gas_used": None, "block_number": None, "transaction_hash": None}

    summary = [{
        "events_generated": len(events),
        "batch_id": bundle["batch_id"],
        "merkle_root": bundle["merkle_root"],
        "merkle_depth_full_batch": bundle["merkle_depth"],
        "functional_check_pass_rate_percent": round(sum(1 for r in attacks if r["detected"]) / len(attacks) * 100, 2),
        "functional_checks_passed": sum(1 for r in attacks if r["detected"]),
        "functional_checks_total": len(attacks),
        "offchain_bundle_sha256": offchain_hash,
        "custody_actions": len(custody),
        "custody_valid": custody_check["valid"],
        "digital_twin_state": twin_snapshot["state"],
        "blockchain_status": receipt["status"],
    }]

    # CSV
    write_csv(base / "csv/final_summary.csv", summary)
    write_csv(base / "csv/scalability_results.csv", scalability)
    write_csv(base / "csv/functional_integrity_checks.csv", attacks)
    # Backward-compatible filename retained for existing dashboard consumers.
    write_csv(base / "csv/attack_detection_matrix.csv", attacks)
    write_csv(base / "csv/event_type_distribution.csv", rows_from_counter(event_dist, "event_type"))
    write_csv(base / "csv/severity_distribution.csv", rows_from_counter(severity_dist, "severity"))
    write_csv(base / "csv/digital_twin_snapshot.csv", [twin_snapshot])
    write_csv(base / "csv/chain_of_custody.csv", custody)
    write_csv(base / "csv/device_registry.csv", DEVICE_REGISTRY)
    write_csv(base / "csv/architecture_zones.csv", architecture_zones())
    write_csv(base / "csv/requirements_traceability.csv", requirements_traceability())
    write_csv(base / "csv/threat_model_matrix.csv", threat_model_matrix())
    write_csv(base / "csv/blockchain_receipt.csv", [receipt])

    # Excel
    write_excel(base / "excel/aquaforenchain_results.xlsx", {
        "summary": summary,
        "scalability": scalability,
        "attacks": attacks,
        "devices": DEVICE_REGISTRY,
        "custody": custody[:100],
    })

    # JSON/raw
    for rel, data in [
        ("raw/events.json", events), ("raw/evidence_bundle.json", bundle), ("raw/chain_of_custody.json", custody),
        ("json/final_summary.json", summary), ("json/scalability_results.json", scalability),
        ("json/functional_integrity_checks.json", attacks), ("json/attack_detection_matrix.json", attacks), ("blockchain/receipts/blockchain_receipt.json", receipt)
    ]:
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # data mirrors requested dirs
    Path("data/raw_events/enhanced_events.json").write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/evidence_store/evidence_bundle.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    (base / "raw/evidence_bundle.canonical.json").write_text(canonical_bundle, encoding="utf-8")
    (base / "blockchain/payloads/bundle_commitment.json").write_text(json.dumps({
        "algorithm": "SHA-256",
        "canonicalization": "json.dumps(sort_keys=True,separators=(\",\",\":\"),ensure_ascii=False) UTF-8",
        "canonical_bundle_file": "results/raw/evidence_bundle.canonical.json",
        "offchain_bundle_sha256": offchain_hash
    }, indent=2), encoding="utf-8")

    # LaTeX tables
    write_latex_table(base / "latex/table_final_summary.tex", summary, "AquaForenChain final experiment summary", "tab:final-summary")
    write_latex_table(base / "latex/table_scalability_results.tex", scalability, "Cryptographic scalability results", "tab:scalability", max_rows=20)
    write_latex_table(base / "latex/table_attack_detection.tex", attacks, "Functional post-capture integrity checks", "tab:attacks")
    write_latex_table(base / "latex/table_architecture_zones.tex", architecture_zones(), "AquaForenChain architecture zones", "tab:architecture-zones")
    write_latex_table(base / "latex/table_requirements_traceability.tex", requirements_traceability(), "Requirement-to-validation traceability", "tab:req-trace")

    # Figures
    write_simple_svg_bar(base / "figures/merkle_generation_vs_batch_size.svg", scalability, "batch_size", "merkle_generation_ms", "Merkle generation time vs batch size")
    write_simple_svg_bar(base / "figures/verification_time_vs_batch_size.svg", scalability, "batch_size", "verification_ms", "Verification time vs batch size")
    write_simple_svg_bar(base / "figures/commitment_reduction_vs_batch_size.svg", scalability, "batch_size", "commitment_reduction_ratio", "Commitment reduction ratio")
    write_simple_svg_bar(base / "figures/event_type_distribution.svg", rows_from_counter(event_dist, "event_type"), "event_type", "count", "Event type distribution")

    # Reports
    lines = [f"Events generated: {len(events)}", f"Merkle root: {bundle['merkle_root']}", f"Functional integrity checks: {summary[0]['functional_checks_passed']}/{summary[0]['functional_checks_total']}", f"Off-chain bundle SHA-256: {offchain_hash}", f"Custody valid: {custody_check['valid']}", f"Blockchain status: {receipt['status']}"]
    write_report(base / "reports/final_experiment_report.pdf", "AquaForenChain Final Experiment Report", lines)
    (base / "reports/final_experiment_report.md").write_text("# AquaForenChain Final Experiment Report\n\n" + "\n".join(f"- {line}" for line in lines) + "\n", encoding="utf-8")

    return {"summary": summary[0], "paths": {"results": str(base), "database": "data/events.db"}}


def parse_batch_sizes(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(',') if x.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AquaForenChain final structured prototype")
    parser.add_argument("--events", type=int, default=5000)
    parser.add_argument("--batch-sizes", default="25,50,100,250,500,1000,2500,5000")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--anchor-on-chain", action="store_true")
    args = parser.parse_args()
    result = run_experiment(args.events, parse_batch_sizes(args.batch_sizes), args.seed, args.output_dir, args.anchor_on_chain)
    print("AquaForenChain structured prototype completed")
    print(json.dumps(result["summary"], indent=2))
    print(f"Outputs: {result['paths']['results']}")


if __name__ == "__main__":
    main()
