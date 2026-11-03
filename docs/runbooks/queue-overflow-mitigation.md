# Runbook: Job Queue Overflow Mitigation

## Objective
Handle sudden bursts of scan submissions without memory exhaustion or request drops.

## Symptoms
- API returns `429 Too Many Requests` or `503 Service Unavailable` on scan submission.
- `BoundedJobQueue` reaches capacity (default: 200 items).

## Actions
1. Review active scans and cancel duplicate or stale requests.
2. Increase worker concurrency if CPU and I/O permit:
   ```bash
   export SBH_WORKER_CONCURRENCY=4
   ```
3. Prioritize urgent investigations using `TaskPriority.HIGH` or `TaskPriority.CRITICAL`.
