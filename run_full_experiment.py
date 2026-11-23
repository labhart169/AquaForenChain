"""
AquaForenChain – Full Experiment Runner
Generates all raw results + high-quality matplotlib figures for the article.
Run from project root:
    python run_full_experiment.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

# ─── ensure project root is on PYTHONPATH ────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ─── core experiment ─────────────────────────────────────────────────────────
from backend.main import run_experiment, parse_batch_sizes

EVENTS      = 5000
SEED        = 42
BATCH_SIZES = [25, 50, 100, 250, 500, 1000, 2500, 5000]
OUTPUT_DIR  = ROOT / "results"

print("=" * 62)
print("  AquaForenChain – Full Experiment")
print(f"  Events: {EVENTS}  |  Seed: {SEED}  |  Batches: {BATCH_SIZES}")
print("=" * 62)

t_start = time.perf_counter()
result = run_experiment(
    events_count=EVENTS,
    batch_sizes=BATCH_SIZES,
    seed=SEED,
    output_dir=str(OUTPUT_DIR),
    anchor_on_chain=False,
)
elapsed = time.perf_counter() - t_start

summary = result["summary"]
print("\n✅  Core experiment completed in {:.2f}s".format(elapsed))
print(json.dumps(summary, indent=2))

# ─── load generated CSVs ─────────────────────────────────────────────────────
import csv

def load_csv(rel: str):
    p = OUTPUT_DIR / rel
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

scalability  = load_csv("csv/scalability_results.csv")
attacks      = load_csv("csv/attack_detection_matrix.csv")
event_dist   = load_csv("csv/event_type_distribution.csv")
severity_d   = load_csv("csv/severity_distribution.csv")
custody_rows = load_csv("csv/chain_of_custody.csv")
devices      = load_csv("csv/device_registry.csv")
arch_zones   = load_csv("csv/architecture_zones.csv")

# ─── matplotlib figures ───────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("⚠  matplotlib not found – skipping high-quality figures")

FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = {
    "blue":   "#1a73e8",
    "green":  "#34a853",
    "orange": "#fa7b17",
    "red":    "#ea4335",
    "purple": "#7b2ff7",
    "teal":   "#00bfa5",
    "gray":   "#5f6368",
    "bg":     "#f8f9fa",
}

def savefig(name: str):
    p = FIG_DIR / name
    plt.savefig(p, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"   📊 {name}")

if HAS_MPL:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.grid":          True,
        "grid.alpha":         0.35,
        "axes.labelsize":     12,
        "xtick.labelsize":    10,
        "ytick.labelsize":    10,
        "legend.fontsize":    10,
        "figure.dpi":         150,
    })

    # ── helper ──────────────────────────────────────────────────────────────
    def sc_x(rows, key):
        return [int(r[key]) for r in rows]

    def sc_y(rows, key):
        return [float(r[key]) for r in rows]

    # ── Fig 1 : Merkle generation time vs batch size ─────────────────────────
    if scalability:
        fig, ax = plt.subplots(figsize=(7, 4))
        xs = sc_x(scalability, "batch_size")
        ys = sc_y(scalability, "merkle_generation_ms")
        ax.plot(xs, ys, "o-", color=PALETTE["blue"], linewidth=2.2, markersize=7, label="Merkle build time")
        ax.fill_between(xs, ys, alpha=0.12, color=PALETTE["blue"])
        ax.set_xlabel("Batch size (number of events)")
        ax.set_ylabel("Merkle tree generation time (ms)")
        ax.set_title("Fig. 1 – Merkle Tree Generation Time vs Batch Size", fontweight="bold")
        ax.set_xscale("log")
        ax.legend()
        savefig("fig1_merkle_generation_time.png")

    # ── Fig 2 : Verification time vs batch size ──────────────────────────────
    if scalability:
        fig, ax = plt.subplots(figsize=(7, 4))
        xs = sc_x(scalability, "batch_size")
        ys = sc_y(scalability, "verification_ms")
        ax.plot(xs, ys, "s-", color=PALETTE["green"], linewidth=2.2, markersize=7, label="Proof verification time")
        ax.fill_between(xs, ys, alpha=0.12, color=PALETTE["green"])
        ax.set_xlabel("Batch size (number of events)")
        ax.set_ylabel("Verification time (ms)")
        ax.set_title("Fig. 2 – Merkle Proof Verification Time vs Batch Size", fontweight="bold")
        ax.set_xscale("log")
        ax.legend()
        savefig("fig2_verification_time.png")

    # ── Fig 3 : Commitment reduction ratio ──────────────────────────────────
    if scalability:
        fig, ax = plt.subplots(figsize=(7, 4))
        xs = sc_x(scalability, "batch_size")
        crr = sc_y(scalability, "commitment_reduction_ratio")
        ax.bar(range(len(xs)), crr, color=PALETTE["orange"], alpha=0.85, edgecolor="white", linewidth=0.8)
        ax.set_xticks(range(len(xs)))
        ax.set_xticklabels([str(x) for x in xs], rotation=25)
        ax.set_xlabel("Batch size (number of events)")
        ax.set_ylabel("Commitment reduction ratio (N:1)")
        ax.set_title("Fig. 3 – Blockchain Commitment Reduction Ratio", fontweight="bold")
        for i, v in enumerate(crr):
            ax.text(i, v + max(crr)*0.01, f"{v:.0f}×", ha="center", va="bottom", fontsize=9, color=PALETTE["gray"])
        savefig("fig3_commitment_reduction.png")

    # ── Fig 4 : Merkle depth vs batch size ───────────────────────────────────
    if scalability:
        fig, ax = plt.subplots(figsize=(7, 4))
        xs = sc_x(scalability, "batch_size")
        depth = sc_y(scalability, "merkle_depth")
        # theoretical log2
        log2_vals = [math.log2(x) for x in xs]
        ax.plot(xs, depth, "D-", color=PALETTE["purple"], linewidth=2.2, markersize=7, label="Actual depth")
        ax.plot(xs, log2_vals, "--", color=PALETTE["gray"], linewidth=1.5, label="⌈log₂(N)⌉ theoretical")
        ax.set_xlabel("Batch size (number of events)")
        ax.set_ylabel("Merkle tree depth (levels)")
        ax.set_title("Fig. 4 – Merkle Tree Depth vs Batch Size", fontweight="bold")
        ax.set_xscale("log")
        ax.legend()
        savefig("fig4_merkle_depth.png")

    # ── Fig 5 : On-chain bytes comparison ────────────────────────────────────
    if scalability:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        xs   = sc_x(scalability, "batch_size")
        direct = [int(r["onchain_bytes_direct_sha256"]) for r in scalability]
        merkle = [int(r["onchain_bytes_merkle_root"]) for r in scalability]
        x_idx = np.arange(len(xs))
        width = 0.35
        ax.bar(x_idx - width/2, direct, width, label="Direct SHA-256 (all hashes)", color=PALETTE["red"],   alpha=0.82)
        ax.bar(x_idx + width/2, merkle, width, label="Merkle root only (32 B)",      color=PALETTE["teal"],  alpha=0.82)
        ax.set_xticks(x_idx)
        ax.set_xticklabels([str(x) for x in xs], rotation=25)
        ax.set_xlabel("Batch size (number of events)")
        ax.set_ylabel("On-chain storage (bytes)")
        ax.set_title("Fig. 5 – On-Chain Storage: Direct vs Merkle Anchoring", fontweight="bold")
        ax.legend()
        ax.set_yscale("log")
        savefig("fig5_onchain_bytes_comparison.png")

    # ── Fig 6 : Event type distribution ──────────────────────────────────────
    if event_dist:
        labels = [r["event_type"].replace("_", "\n") for r in event_dist]
        counts = [int(r["count"]) for r in event_dist]
        colors = [PALETTE["blue"], PALETTE["green"], PALETTE["orange"], PALETTE["red"],
                  PALETTE["purple"], PALETTE["teal"], PALETTE["gray"], "#e91e63", "#ff9800", "#795548"]
        fig, ax = plt.subplots(figsize=(10, 4.5))
        bars = ax.bar(range(len(labels)), counts, color=colors[:len(labels)], alpha=0.88, edgecolor="white")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("Number of events")
        ax.set_title("Fig. 6 – SCADA Event Type Distribution (N=5000)", fontweight="bold")
        for bar, c in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(c),
                    ha="center", va="bottom", fontsize=9)
        savefig("fig6_event_type_distribution.png")

    # ── Fig 7 : Severity distribution ────────────────────────────────────────
    if severity_d:
        sev_colors = {"LOW": PALETTE["green"], "MEDIUM": PALETTE["orange"],
                      "HIGH": PALETTE["red"], "CRITICAL": "#9c0000"}
        labels = [r["severity"] for r in severity_d]
        counts = [int(r["count"]) for r in severity_d]
        cols   = [sev_colors.get(l, PALETTE["gray"]) for l in labels]
        fig, ax = plt.subplots(figsize=(6, 4))
        wedges, texts, autotexts = ax.pie(
            counts, labels=labels, colors=cols, autopct="%1.1f%%",
            startangle=140, pctdistance=0.78,
            wedgeprops=dict(edgecolor="white", linewidth=1.8))
        for at in autotexts:
            at.set_fontsize(11)
        ax.set_title("Fig. 7 – Event Severity Distribution", fontweight="bold")
        savefig("fig7_severity_distribution.png")

    # ── Fig 8 : Attack detection matrix ─────────────────────────────────────
    if attacks:
        scenarios = [r["scenario"] for r in attacks]
        detected  = [1 if str(r.get("detected","")).lower() in ("true","1","yes") else 0 for r in attacks]
        results   = [r.get("result","?") for r in attacks]
        fig, ax = plt.subplots(figsize=(9, 4))
        bar_colors = [PALETTE["green"] if d else PALETTE["red"] for d in detected]
        bars = ax.barh(range(len(scenarios)), detected, color=bar_colors, alpha=0.88, edgecolor="white", height=0.55)
        ax.set_yticks(range(len(scenarios)))
        ax.set_yticklabels(scenarios, fontsize=11)
        ax.set_xlim(0, 1.4)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Not Detected", "Detected"])
        ax.set_title("Fig. 8 – Forensic Attack Detection Matrix", fontweight="bold")
        for i, (d, res) in enumerate(zip(detected, results)):
            ax.text(d + 0.03, i, res, va="center", fontsize=11,
                    color=PALETTE["green"] if res == "PASS" else PALETTE["red"], fontweight="bold")
        savefig("fig8_attack_detection_matrix.png")

    # ── Fig 9 : Proof length vs batch size ───────────────────────────────────
    if scalability:
        fig, ax = plt.subplots(figsize=(7, 4))
        xs = sc_x(scalability, "batch_size")
        pl = sc_y(scalability, "proof_length")
        ax.plot(xs, pl, "^-", color=PALETTE["teal"], linewidth=2.2, markersize=8, label="Proof length (hashes)")
        ax.set_xlabel("Batch size (number of events)")
        ax.set_ylabel("Merkle proof length (number of hashes)")
        ax.set_title("Fig. 9 – Merkle Proof Length vs Batch Size", fontweight="bold")
        ax.set_xscale("log")
        ax.legend()
        savefig("fig9_proof_length.png")

    # ── Fig 10 : Combined scalability – dual-axis ─────────────────────────────
    if scalability:
        fig, ax1 = plt.subplots(figsize=(9, 5))
        xs   = sc_x(scalability, "batch_size")
        gen  = sc_y(scalability, "merkle_generation_ms")
        verif = sc_y(scalability, "verification_ms")
        color1 = PALETTE["blue"]
        color2 = PALETTE["orange"]
        ln1 = ax1.plot(xs, gen, "o-", color=color1, linewidth=2.2, markersize=7, label="Build time (ms)")
        ax1.set_xlabel("Batch size (number of events)")
        ax1.set_ylabel("Merkle build time (ms)", color=color1)
        ax1.tick_params(axis="y", labelcolor=color1)
        ax1.set_xscale("log")
        ax2 = ax1.twinx()
        ln2 = ax2.plot(xs, verif, "s--", color=color2, linewidth=2.2, markersize=7, label="Verify time (ms)")
        ax2.set_ylabel("Proof verification time (ms)", color=color2)
        ax2.tick_params(axis="y", labelcolor=color2)
        lns = ln1 + ln2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc="upper left")
        ax1.set_title("Fig. 10 – Cryptographic Performance: Build & Verify Times", fontweight="bold")
        savefig("fig10_combined_scalability.png")

    print(f"\n   ✅  All matplotlib figures saved to: {FIG_DIR}\n")

# ─── print rich summary table ─────────────────────────────────────────────────
print("\n" + "=" * 62)
print("  EXPERIMENT SUMMARY")
print("=" * 62)
for k, v in summary.items():
    print(f"  {k:<40} {v}")

print("\n" + "=" * 62)
print("  SCALABILITY RESULTS")
print("=" * 62)
headers = ["batch_size","merkle_depth","proof_length","merkle_generation_ms","verification_ms","commitment_reduction_ratio"]
hdr = " | ".join(f"{h:<28}" for h in headers)
print(hdr)
print("-" * len(hdr))
for r in scalability:
    row_str = " | ".join(f"{str(r.get(h,'')):<28}" for h in headers)
    print(row_str)

print("\n" + "=" * 62)
print("  ATTACK DETECTION MATRIX")
print("=" * 62)
for r in attacks:
    status = "✅ PASS" if r.get("result") == "PASS" else "❌ FAIL"
    print(f"  {status}  {r.get('scenario',''):<30}  {r.get('mechanism','')}")

print("\n" + "=" * 62)
print(f"  Total time: {elapsed:.2f}s")
print(f"  All outputs: {OUTPUT_DIR}")
print("=" * 62)
