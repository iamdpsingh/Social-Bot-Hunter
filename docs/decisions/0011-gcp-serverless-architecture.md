# ADR-0011: Local Virtualenv Self-Contained Runtime Architecture

**Status:** accepted (supersedes initial GCP cloud proposal)

**Context.** The system was originally considered for Google Cloud Platform managed services. However, due to cloud cost constraints, expiring free-tier quotas, and the requirement for completely reproducible offline operation, the platform must run completely self-contained in a local Python virtual environment (`.venv`) without cloud dependencies or external paid hosting.

**Decision.** Deploy and operate the target architecture locally within a standard Python virtual environment:
1. **Compute**: FastAPI backend service served via Uvicorn (`127.0.0.1:8000`) and decoupled local worker processes running directly within the local `.venv`.
2. **Database**: Local SQLite database for rapid zero-configuration development and automated testing; optional local PostgreSQL 16 (via local brew service or container) using the portable SQL schema in `db/migrations/0001_init.sql`.
3. **File Storage**: Local filesystem directories for raw dataset snapshots (`data/snapshots/`), trained ML models (`data/models/`), and investigation exports (`data/exports/`), governed by automated local retention sweeps (`sbh retention-sweep`).
4. **Queue & Scheduling**: Local in-process and multi-process background worker queues with graceful shutdown handling (`SIGINT`/`SIGTERM`), removing dependencies on cloud task queues.
5. **Security & Secrets**: Secure local `.env` configuration file guarded by `.gitignore` with strict exclusion of sensitive credentials from version control.
6. **Frontend**: Next.js dashboard running locally via Node.js (`127.0.0.1:3000`), connecting directly to the local FastAPI backend.

**Alternatives.**
- GCP Serverless (Cloud Run, Cloud SQL, Cloud Storage): Introduces recurring hosting costs, vendor lock-in, and billing overhead when free tier quotas expire.
- Docker-only requirement: Imposes heavy container engine overhead for pure Python analytics. Python virtual environments (`.venv`) provide maximum portability across macOS, Linux, and Windows.

**Consequences.** Zero cloud infrastructure bills, zero cloud dependency, 100% reproducible offline local execution, simplified developer ergonomics, and instant local verification.
