# RUNBOOK-0106: Air-Gapped Offline Investigation Workflow

## Scope & Target
Operating Social Bot Hunter in classified or isolated air-gapped environments.

## Operational Procedure
1. Enable offline mode: `export SBH_OFFLINE_MODE=1`
2. Mount raw investigation archive into `data/snapshots/`.
3. Ingest archive: `python -m sbh import data/snapshots/archive.zip --actor investigator_1`
4. Verify analysis: `python -m sbh report <scan_id>`
5. Export Cytoscape graph package for offline viewing: `python -m sbh export <scan_id> --format json`
