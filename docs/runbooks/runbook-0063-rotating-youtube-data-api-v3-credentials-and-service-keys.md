# RUNBOOK-0063: Rotating YouTube Data API v3 Credentials and Service Keys

## Severity
P2 — High Operational Impact

## Purpose
Standard operating procedure for operators managing live platform integrations and API quota ceilings.

## Procedure
1. **Diagnosis**: Provision new API key in GCP API Credentials, update SBH_YOUTUBE_API_KEY environment variable, and verify health.
2. **Mitigation**: Apply operational circuit-breaker or rotate credentials as documented.
3. **Verification**: Execute `sbh adapters probe` or trigger a test request to confirm resolution.
