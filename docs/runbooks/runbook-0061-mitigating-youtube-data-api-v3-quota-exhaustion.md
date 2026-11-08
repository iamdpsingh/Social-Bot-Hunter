# RUNBOOK-0061: Mitigating YouTube Data API v3 Quota Exhaustion

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Verify daily quota consumption in GCP console, identify high-frequency scans, and activate batch caching.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
