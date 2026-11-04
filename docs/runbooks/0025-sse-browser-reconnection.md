# Runbook 0025: Diagnosing Browser EventSource Drops

## Objective
Troubleshoot interrupted scan progress streams.

## Inspection
Check browser Network tab for `GET /api/v1/scans/{id}/events`. Verify `text/event-stream` header and `Last-Event-ID` header on reconnect.
