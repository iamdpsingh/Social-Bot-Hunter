# Local Virtualenv Deployment & Runtime Guide

**Target Architecture:** Self-contained execution in a local Python virtual environment (`.venv`).  
**Status:** Local execution is active and tested. The core pipeline, CLI, analytical engine, and FastAPI REST API run entirely on the local machine with zero paid cloud dependencies.

---

## 1. Local Environment Philosophy

Social Bot Hunter is engineered to be 100% operational offline and locally:
1. **Zero Cloud Costs**: Does not require GCP, AWS, Azure, or paid cloud APIs to run investigations, score accounts, or visualize coordinated networks.
2. **Local Virtual Environment**: Managed via standard Python 3.11+ `venv`, eliminating heavy virtual machine or mandatory container requirements.
3. **Local Storage**: All data, snapshots, models, and investigation exports reside in local filesystem directories (`./data/`).
4. **Flexible Database**: Runs out-of-the-box on SQLite (`./sbh-dev.sqlite`) for development and testing; seamlessly switches to a local PostgreSQL 16 instance when scaling up.

---

## 2. Quickstart Setup

### Step 1: Create and activate virtual environment

```bash
# From repository root
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```bash
# Core package in editable mode with development, API, and PostgreSQL extras
pip install --upgrade pip
pip install -e ".[dev,api,postgres]"
```

### Step 3: Configure local environment

```bash
cp .env.example .env
# Edit .env as needed; defaults work immediately for SQLite
```

Default configuration in `.env`:
```ini
SBH_ENV=development
SBH_DATABASE_URL=sqlite:///./sbh-dev.sqlite
SBH_CONFIG_PATH=src/sbh/resources/detection.v1.yaml
SBH_MIGRATIONS_DIR=db/migrations
SBH_LOG_LEVEL=INFO

# Local Storage
SBH_SNAPSHOT_DIR=./data/snapshots
SBH_EXPORT_DIR=./data/exports
SBH_MODELS_DIR=./data/models
```

### Step 4: Run database migrations

```bash
python -m sbh migrate --db ./sbh-dev.sqlite
```

### Step 5: Verify with synthetic demo pipeline

```bash
python -m sbh demo --db ./sbh-dev.sqlite
```

---

## 3. Running Services Locally

### 3.1 FastAPI REST API Server

Start the REST API on `http://127.0.0.1:8000`:

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --reload
```

- Interactive OpenAPI Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`
- Platform capabilities: `http://127.0.0.1:8000/api/v1/capabilities`

### 3.2 Next.js Dashboard (Frontend Workspace)

Run the investigation dashboard on `http://127.0.0.1:3000`:

```bash
cd apps/dashboard
npm install
npm run dev
```

The dashboard communicates with the local FastAPI backend at `http://127.0.0.1:8000/api/v1`.

### 3.3 Background Processing & Async Scans

For long-running investigations, background tasks run asynchronously:
- In development: FastAPI's background task engine handles asynchronous imports and analysis.
- Multi-process worker runner: Executed via `python -m sbh worker` (Phase 4).

### 3.4 Convenience Local Runner

A unified runner script (`scripts/run_local.sh`) launches both backend and frontend services together:

```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

---

## 4. Local Database Operations & Migrations

### Applying Migrations
- Migration files are versioned in `db/migrations/NNNN_name.sql`.
- Applied in strict order by `python -m sbh migrate`; each execution runs in a transaction and records a SHA-256 checksum in `schema_migrations`.
- Applied files are immutable. Schema adjustments must be added as a new migration file.

### Local Database Backup & Restore
Before running experimental migrations or destructive retention sweeps:

**For SQLite:**
```bash
# Backup
cp sbh-dev.sqlite sbh-dev.sqlite.backup.$(date +%Y%m%d%H%M%S)

# Restore
cp sbh-dev.sqlite.backup.YYYYMMDDHHMMSS sbh-dev.sqlite
```

**For Local PostgreSQL:**
```bash
# Backup
pg_dump -U sbh_user -d sbh -F c -b -v -f ./data/backups/sbh_$(date +%Y%m%d%H%M%S).dump

# Restore
pg_restore -U sbh_user -d sbh -v ./data/backups/sbh_YYYYMMDDHHMMSS.dump
```

### Rollback Strategy
Migrations are forward-only. To roll back an erroneous migration:
1. Restore the pre-migration database snapshot, or
2. Write a new reversing migration (`NNNN_revert_name.sql`) and run `python -m sbh migrate`.
3. If a migration errors during execution, the transaction rolls back automatically (tested on SQLite).

---

## 5. Local Storage & File Directories

Raw datasets, ML models, and exported reports are kept in project-local directories:
- `data/snapshots/`: Archived raw dataset packages and payloads with content hashes.
- `data/models/`: Serialized rulesets and trained Scikit-learn models (`.joblib`).
- `data/exports/`: Investigation evidence reports, CSV exports, and Cytoscape JSON bundles.
- `data/samples/`: Versioned test fixtures and benchmark datasets.

All export and snapshot directories are covered by the automated retention sweep:
```bash
python -m sbh retention-sweep --days 90
```

---

## 6. Continuous Integration (CI)

`.github/workflows/ci.yml` runs automated checks on push and pull request:
- Ruff formatting and lint check across `src/`, `tests/`, `services/`.
- Mypy static type verification.
- Documentation drift verification (`python -m sbh docs`).
- Unit, data-quality, security, and model evaluation test suites on SQLite.
- PostgreSQL backend integration test using an ephemeral PostgreSQL 16 container service.
