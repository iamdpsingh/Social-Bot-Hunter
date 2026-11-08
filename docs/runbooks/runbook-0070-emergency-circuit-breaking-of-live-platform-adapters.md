# RUNBOOK-0070: Emergency Circuit-Breaking of Live Platform Adapters

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Switch adapter mode to NotConfiguredAdapter via environment flag SBH_DISABLE_LIVE_ADAPTERS during platform outages.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
