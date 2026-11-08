# RUNBOOK-0062: Resolving X API v2 HTTP 429 Rate-Limit Cascades

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Inspect EndpointRateLimiter metrics, identify burst scans, and apply worker backoff delays.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
