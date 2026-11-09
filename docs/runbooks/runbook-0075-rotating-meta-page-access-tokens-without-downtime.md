# RUNBOOK-0075: Rotating Meta Page Access Tokens Without Service Interruption

## Summary
Zero-downtime token rollover before 60-day expiry.

## Procedure
1. Issue new token from Meta Graph API Explorer.
2. Update `.env` and signal FastAPI process.
3. Validate with `/api/v1/adapters/quotas`.