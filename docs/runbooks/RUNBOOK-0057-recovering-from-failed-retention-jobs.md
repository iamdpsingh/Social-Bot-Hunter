# RUNBOOK-0057: Recovering from Interrupted Data Retention Jobs

## Purpose
Recover database consistency if a data retention purge was terminated mid-flight.

## Procedure
1. Retention purge operates inside an atomic database transaction.
2. Check `schema_migrations` and run integrity check: `PRAGMA integrity_check`.
3. Re-run `get_retention_stats` to verify storage metrics.
