# RUNBOOK-0087: Calibrating LinkedIn Daily Quota and Rate Limits

## Purpose
Monitor LinkedIn Community Management API quota consumption (2,500 daily units, 100 req/min).

## Steps
1. Check `/api/v1/adapters/quotas` for LinkedIn status.
2. Observe `quota_remaining` and `units_used`.
3. Back off automated probe workers if quota reaches <10% remaining.
