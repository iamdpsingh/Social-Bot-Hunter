# Runbook 0030: Frontend API Error Handling and Triage

## Objective
Troubleshoot 401 Unauthorized, 404 Not Found, and 429 Rate Limit responses.

## Actions
- 401: Refresh JWT bearer token via `/auth/refresh`
- 429: Read `Retry-After` header and display countdown toast
- 500: Check FastAPI access logs and correlation `X-Trace-ID`
