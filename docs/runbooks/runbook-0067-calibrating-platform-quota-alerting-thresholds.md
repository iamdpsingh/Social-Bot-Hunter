# RUNBOOK-0067: Calibrating Platform Quota Alerting Thresholds

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Adjust warning_ratio in PlatformQuotaTracker to alert teams when daily API consumption hits 80% and 90%.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
