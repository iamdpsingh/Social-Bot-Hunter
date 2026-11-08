# RUNBOOK-0066: Replaying Failed Live Ingestion Tasks

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Extract target account identifier from failed scan, verify adapter health, and re-enqueue scan job with exponential retry.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
