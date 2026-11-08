# RUNBOOK-0069: Auditing Adapter Request Logs for PII Sanitization

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Ensure auth tokens, bearer headers, and private email addresses are scrubbed from telemetry logs.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
