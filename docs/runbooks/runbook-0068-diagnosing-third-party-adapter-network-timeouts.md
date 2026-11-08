# RUNBOOK-0068: Diagnosing Third-Party Adapter Network Timeouts

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Inspect proxy latency, check remote platform status dashboards, and verify SSL certificate chains.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
