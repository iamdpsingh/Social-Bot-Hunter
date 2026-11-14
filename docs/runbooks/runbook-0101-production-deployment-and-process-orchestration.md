# RUNBOOK-0101: Production Deployment & Process Orchestration

## Scope & Target
Local `.venv` single-host process orchestration via `scripts/run_local.sh`.

## Operational Procedure
1. Verify Python 3.12+ virtual environment is active: `python -m sbh doctor`
2. Start process supervisor: `./scripts/run_local.sh`
3. Verify processes:
   - FastAPI REST API on `http://localhost:8000/api/v1/health`
   - Next.js Dashboard on `http://localhost:3000`
   - Background worker processing jobs
4. For graceful shutdown, send `SIGINT` (Ctrl+C). The supervisor terminates children cleanly within 5 seconds.
