"""
AquaForenChain Enhanced API – serves the web dashboard and all data endpoints.
Run with: python serve_dashboard.py
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RESULTS_DIR = ROOT / "results"
DB_PATH     = ROOT / "data" / "events.db"


def _load_json(rel: str):
    p = RESULTS_DIR / rel
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _load_csv_as_list(rel: str):
    import csv
    p = RESULTS_DIR / rel
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

if not HAS_FASTAPI:
    print("FastAPI not found. Installing...")
    os.system(f"{sys.executable} -m pip install fastapi uvicorn -q")
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn

app = FastAPI(
    title="AquaForenChain Dashboard API",
    description="Forensic-Ready Ethereum + Digital-Twin for Smart-City Water Infrastructure",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root():
    dashboard_path = ROOT / "dashboard" / "index.html"
    if dashboard_path.exists():
        return HTMLResponse(dashboard_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AquaForenChain</h1><p>Run enhanced experiment first.</p>")


@app.get("/api/summary")
def api_summary():
    data = _load_json("json/final_summary.json")
    stat = _load_json("json/statistical_analysis.json")
    if data:
        summary = data[0] if isinstance(data, list) else data
        if stat:
            summary["statistical_runs"] = len(stat)
        return summary
    return {"error": "Run the experiment first"}


@app.get("/api/scalability")
def api_scalability():
    return _load_json("json/scalability_results.json") or []


@app.get("/api/statistical")
def api_statistical():
    return _load_json("json/statistical_analysis.json") or []


@app.get("/api/attacks")
def api_attacks():
    return _load_json("json/attack_detection_matrix.json") or []


@app.get("/api/events/distribution")
def api_events_dist():
    return _load_csv_as_list("csv/event_type_distribution.csv")


@app.get("/api/severity/distribution")
def api_severity_dist():
    return _load_csv_as_list("csv/severity_distribution.csv")


@app.get("/api/digital_twin")
def api_digital_twin():
    rows = _load_csv_as_list("csv/digital_twin_snapshot.csv")
    return rows[0] if rows else {}


@app.get("/api/custody")
def api_custody():
    data = _load_json("json/chain_of_custody_summary.json")
    if data:
        return data
    rows = _load_csv_as_list("csv/chain_of_custody.csv")
    return {"total": len(rows), "valid": True, "sample": rows[:5]}


@app.get("/api/devices")
def api_devices():
    return _load_csv_as_list("csv/device_registry.csv")


@app.get("/api/gas")
def api_gas():
    return _load_json("json/gas_cost_estimation.json") or []


@app.get("/api/gas/deployment")
def api_gas_deployment():
    return _load_json("json/gas_deployment_costs.json") or []


@app.get("/api/comparative")
def api_comparative():
    return _load_json("json/comparative_analysis.json") or []


@app.get("/api/mitre")
def api_mitre():
    return _load_json("json/mitre_attack_mapping.json") or []


@app.get("/api/throughput")
def api_throughput():
    return _load_json("json/hashing_throughput.json") or []


@app.get("/api/overhead")
def api_overhead():
    return _load_json("json/forensic_overhead.json") or []


@app.get("/api/sensitivity")
def api_sensitivity():
    return _load_json("json/sensitivity_analysis.json") or []


@app.get("/api/privacy")
def api_privacy():
    return _load_json("json/privacy_analysis.json") or []


@app.get("/api/smart_city")
def api_smart_city():
    return _load_json("json/smart_city_scenarios.json") or []


@app.get("/api/requirements")
def api_requirements():
    return _load_json("json/requirements_traceability.json") or []


@app.get("/api/blockchain/receipt")
def api_blockchain_receipt():
    return _load_json("blockchain/receipts/blockchain_receipt.json") or {}


@app.get("/api/figures")
def api_figures():
    figs = []
    fig_dir = RESULTS_DIR / "figures"
    if fig_dir.exists():
        for f in sorted(fig_dir.glob("*.png")):
            figs.append({"name": f.name, "path": f"/figures/{f.name}", "size_kb": round(f.stat().st_size / 1024, 1)})
    return figs


@app.get("/figures/{filename}")
def serve_figure(filename: str):
    p = RESULTS_DIR / "figures" / filename
    if p.exists():
        return FileResponse(str(p), media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  AquaForenChain Dashboard v2.0")
    print("  http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
