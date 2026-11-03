# Runbook: Background Worker Troubleshooting

## Objective
Diagnose and resolve background job worker stalls, high memory usage, and queue processing failures.

## Symptoms
- Scans remain in `pending` status indefinitely.
- Worker heartbeat timestamps do not advance.
- CPU utilization is pegged at 100% on worker threads.

## Diagnostic Steps
1. Verify worker pool status via `sbh status` or API `/api/v1/health`.
2. Inspect `scan_checkpoints` to determine the last completed stage.
3. Check application logs for unhandled worker thread exceptions or rate-limit backoff sleeps.

## Remediation
- If a scan is blocked on an external API rate limit, the worker will automatically resume after the backoff window.
- If a scan is deadlocked, invoke `POST /api/v1/scans/{scan_id}/cancel`.
- Restart the API service; pending and cancelled scans can be resumed via `POST /api/v1/scans/{scan_id}/retry`.
