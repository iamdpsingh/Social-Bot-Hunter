# RUNBOOK-0064: Rotating X API v2 Bearer Tokens and Client Secrets

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Regenerate App Bearer Token in X Developer Portal, update SBH_X_BEARER_TOKEN, and trigger preflight probe test.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
