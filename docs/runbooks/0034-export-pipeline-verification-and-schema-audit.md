# Runbook 0034: Export Pipeline Verification and Schema Audit

## Objective
Validate that CSV and JSON export files conform to audit compliance schemas.

## Verification Steps
1. Trigger CSV export: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/scans/{id}/export/csv -o test.csv`.
2. Verify headers: `head -n 1 test.csv` must include `account_id,username,risk_score,risk_band,coverage`.
3. Trigger JSON export: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/scans/{id}/export/json | jq .summary`.
