# Social Bot Hunter (v1.0.0)

[![CI](https://github.com/iamdpsingh/Social-Bot-Hunter/actions/workflows/ci.yml/badge.svg)](https://github.com/iamdpsingh/Social-Bot-Hunter/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.0.0-emerald.svg)](https://github.com/iamdpsingh/Social-Bot-Hunter/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-1600%2B%20passed-brightgreen.svg)](docs/verification/test-matrix-summary.md)

An open-source, production-grade social media investigation and coordinated inauthentic behavior (CIB) detection platform. It ingests multi-platform profile observations, evaluates explainable heuristic indicators and machine learning models, discovers coordinated botrings via text fingerprinting (SimHash) and network topology clustering, and visualizes interactive relationship graphs in Cytoscape.js.

> **Status: Production v1.0.0 Launched (14-Day Delivery Master Plan 100% Completed).**  
> 1,600+ automated test suites passing across Python unit, integration, PostgreSQL 17 backend, OWASP security regression suite, micro-benchmarks, and Next.js 14 Vitest frontend. Zero external paid APIs required; operates 100% locally in an isolated virtual environment (`.venv`).

---

## Key Capabilities

- **Multi-Platform Ingestion**: Standardized adapters and mock datasets for **Twitter/X**, **Bluesky**, **Mastodon**, **Reddit**, and **YouTube**.
- **Explainable Scoring Engine**: Deterministic heuristic rules with signal attribution, coverage percentage, and alternative explanations.
- **Machine Learning Classification**: Leakage-free Scikit-Learn pipeline (Random Forest, Logistic Regression) with calibrated probabilities and published Model Cards.
- **Text Fingerprinting (SimHash)**: 64-bit Hamming distance clustering for duplicate and near-duplicate broadcast campaign detection.
- **Coordinated Network Detection**: Dense clique extraction, bipartite follow-ring analysis, and temporal burst windowing.
- **Interactive Graph Visualization**: Cytoscape.js network canvas in Next.js 14 with cluster convex hulls, ego expansions, and node inspection drawers.
- **Local Venv Orchestration**: Standalone process supervisor (`scripts/run_local.sh`) coordinating FastAPI, worker queues, and frontend in `.venv` with zero cloud dependencies.
- **Hardened Security & Privacy**: SHA-256 HMAC pseudonymization of PII, automated high-entropy secret scanner, OWASP API Top 10 defense matrix, and container security compliance.

---

## Quick Start (Local Environment)

### 1. Prerequisites
- Python 3.12+ (or 3.13)
- Node.js 20+ & npm 10+
- SQLite 3 (or local PostgreSQL 16/17)

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/iamdpsingh/Social-Bot-Hunter.git
cd "Social Bot Hunter"

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -e ".[dev,postgres,api]"

# Install frontend dependencies
cd apps/dashboard && npm install && cd ../..
```

### 3. Run Self-Contained Demo
```bash
# Execute synthetic demo pipeline (generates, ingests, scores, and prints report)
python -m sbh demo --db ./sbh-dev.sqlite
```

### 4. Run System Health & Micro-Benchmarks
```bash
# Execute local subsystem health diagnostics
python -m sbh doctor

# Run latency and throughput micro-benchmarks against SLAs
python -m sbh benchmark --iterations 100
```

### 5. Launch Full Production Platform Locally
```bash
# Launch FastAPI backend, local queue worker, and Next.js dashboard
./scripts/run_local.sh
```
- **Next.js Dashboard**: `http://localhost:3000`
- **FastAPI REST API**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`

---

## System Architecture

```
                  ┌─────────────────────────────────────────┐
                  │       Next.js 14 Dashboard (:3000)      │
                  │   Cytoscape.js Canvas | Evidence Panel  │
                  └───────────────────▲─────────────────────┘
                                      │ REST / WebSocket
                  ┌───────────────────▼─────────────────────┐
                  │       FastAPI REST Service (:8000)      │
                  │  JWT Auth | Rate Limiter | OpenAPI Sync │
                  └───────────────────▲─────────────────────┘
                                      │ IPC / Database
                  ┌───────────────────▼─────────────────────┐
                  │    Local Process Supervisor & Worker    │
                  │ Signal Handling | Bounded Task Concurrency│
                  └─────────▲─────────────────────▲─────────┘
                            │                     │
            ┌───────────────▼────────┐   ┌────────▼──────────────┐
            │   Detection Engine     │   │   Persistence Store   │
            │ Heuristics | ML Models │   │ SQLite / PostgreSQL   │
            │ SimHash | Coordination │   │ Snapshots & Exports   │
            └────────────────────────┘   └───────────────────────┘
```

---

## CLI Reference (`python -m sbh`)

| Command | Description |
| :--- | :--- |
| `demo` | Run complete end-to-end synthetic demo pipeline |
| `doctor` | Run subsystem health diagnostics (database, storage, models) |
| `benchmark` | Execute latency percentile benchmarks against SLA thresholds |
| `migrate` | Apply schema migrations to SQLite or PostgreSQL database |
| `import <path>` | Ingest raw JSON/CSV archives with provenance validation |
| `audit-full` | Run comprehensive security audit scorecard |
| `audit-secrets` | Scan directories for high-entropy hardcoded credentials |
| `audit-privacy` | Scan dataset exports for PII leakage |
| `audit-dependencies` | Audit Python and Node dependencies against advisory database |
| `db-backup` | Create atomic, compressed database snapshot artifact |
| `db-restore` | Safely restore database from verified backup artifact |
| `worker-run` | Run local queue worker processing asynchronous jobs |

---

## Documentation Links

- **14-Day Delivery Master Plan**: [docs/14-day-master-plan.md](docs/14-day-master-plan.md)
- **Specification Section 19 Acceptance Matrix**: [docs/verification/acceptance-matrix.md](docs/verification/acceptance-matrix.md)
- **System Limitations Log**: [docs/verification/limitations-log.md](docs/verification/limitations-log.md)
- **Consolidated Test Matrix Summary**: [docs/verification/test-matrix-summary.md](docs/verification/test-matrix-summary.md)
- **Micro-Benchmark Latency Report**: [docs/benchmarks/latency-report.md](docs/benchmarks/latency-report.md)
- **System Architecture**: [docs/architecture/system-architecture.md](docs/architecture/system-architecture.md)
- **Platform Capability Matrix**: [docs/platform-access-matrix.md](docs/platform-access-matrix.md)
- **Data Dictionary**: [docs/data-dictionary.md](docs/data-dictionary.md)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
