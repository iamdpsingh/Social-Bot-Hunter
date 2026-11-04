# Runbook 0024: SWR Caching and Deduping Interval Tuning

## Objective
Configure polling intervals and deduping thresholds for low-latency updates without API flooding.

## Guidelines
- Health: 10s polling, 5s dedupe
- Scans: 15s polling, mutate on create/cancel/retry
- Audit: 10s polling, 3s dedupe
