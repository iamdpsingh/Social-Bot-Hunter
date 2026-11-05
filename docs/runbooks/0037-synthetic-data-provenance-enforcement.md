# Runbook 0037: Synthetic Data Provenance Enforcement

## Objective
Ensure all mock or demo scan records are flagged with `data_origin: "synthetic"`.

## Verification Steps
1. Inspect database: `sqlite3 data/sbh.db "SELECT id, data_origin FROM scans WHERE data_origin = 'synthetic';"`
2. Verify UI shows amber warning banner on top of scan workspace.
