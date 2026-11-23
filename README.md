# AquaForenChain — Forensic-Ready Ethereum Prototype for Smart Water Infrastructure

Research prototype for blockchain-based forensic evidence anchoring in smart-city water critical infrastructure. Combines SCADA/IoT simulation, digital twin, SHA-256 Merkle batching, and Ethereum smart contracts.

## Project Structure

```text
aquaforenchain/
├── backend/                        # Python backend
│   ├── main.py                     # Main experiment runner
│   ├── simulator/                  # Smart-water SCADA simulator
│   ├── evidence/                   # Evidence collection & Merkle engine
│   ├── blockchain/                 # Blockchain interface
│   ├── storage/                    # Off-chain evidence store
│   ├── experiments/                # Enhanced experiments
│   ├── exports/                    # CSV/JSON/LaTeX/Excel exporters
│   └── api/                        # FastAPI + dashboard routes
├── contracts/                      # Solidity smart contracts (4)
│   ├── DeviceRegistry.sol
│   ├── EvidenceAnchor.sol
│   ├── IncidentManager.sol
│   └── ChainOfCustody.sol
├── scripts/                        # Hardhat scripts
│   ├── deploy.js                   # Deploy all contracts
│   ├── anchor_batch.js             # Anchor evidence batch
│   └── measure_blockchain.js       # Full gas measurement suite
├── dashboard/                      # Glassmorphism web dashboard
├── frontend/                       # React frontend
├── test/                           # Hardhat tests
├── run_enhanced_experiment.py      # Enhanced experiment script
├── run_full_experiment.py          # Full experiment script
├── serve_dashboard.py              # Dashboard server
├── hardhat.config.js               # Hardhat configuration
├── package.json                    # Node.js dependencies
└── requirements.txt                # Python dependencies
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**

## 1. Installation

### Python dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Node.js dependencies (Hardhat / Ethereum)

```powershell
npm install
```

Or double-click `INSTALL_WINDOWS.bat`.

## 2. Run the Blockchain (Hardhat)

**Terminal 1** — Start a local Ethereum node:

```powershell
npx hardhat node
```

Or double-click `START_HARDHAT_NODE_WINDOWS.bat`.

**Terminal 2** — Compile, deploy, and test:

```powershell
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
npx hardhat run scripts/anchor_batch.js --network localhost
npx hardhat run scripts/measure_blockchain.js --network localhost
npx hardhat test
```

Or double-click `RUN_BLOCKCHAIN_WINDOWS.bat`.

## 3. Run the Dashboard

```powershell
$env:PYTHONPATH="."
python serve_dashboard.py
```

Open `http://localhost:8000` — glassmorphism dark-mode interface with real-time SCADA visualization, Merkle tree, attack matrix, chain of custody, and gas costs.

## 4. Run the API Backend

```powershell
$env:PYTHONPATH="."
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Or double-click `RUN_API_WINDOWS.bat`.

## 5. Run the Experiment

Generate all experimental results (CSV, JSON, LaTeX tables, figures, Excel workbooks):

```powershell
$env:PYTHONPATH="."
python -m backend.main --events 5000 --batch-sizes 25,50,100,250,500,1000,2500,5000
```

Results will be generated in a `results/` directory.

## Smart Contracts

| Contract | Description |
|----------|-------------|
| `DeviceRegistry.sol` | Register and manage IoT/SCADA devices |
| `EvidenceAnchor.sol` | Anchor SHA-256 Merkle roots on-chain |
| `IncidentManager.sol` | Record and track security incidents |
| `ChainOfCustody.sol` | Maintain forensic chain of custody |

## License

This project is a research prototype. See the accompanying publication for details.
