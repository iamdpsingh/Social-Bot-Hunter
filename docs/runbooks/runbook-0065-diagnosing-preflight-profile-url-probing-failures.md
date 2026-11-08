# RUNBOOK-0065: Diagnosing Preflight Profile URL Probing Failures

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Check URL grammar in validate_profile_url, confirm entity existence on platform, and review rate limit counters.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
