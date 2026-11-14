# RUNBOOK-0102: Cold-Start System Boot & Health Probing

## Scope & Target
Initial environment bringup from cold storage without active database connections.

## Operational Procedure
1. Execute diagnostic probe: `python -m sbh doctor --json`
2. Verify SQLite integrity: `PRAGMA integrity_check` reports `ok`.
3. Verify storage directories: `data/snapshots/`, `data/exports/`, `data/models/` must be writable with &ge; 500MB headroom.
4. Verify baseline model rules exist in `data/models/`.
5. If any probe reports `UNHEALTHY`, check filesystem permissions before starting the API.
