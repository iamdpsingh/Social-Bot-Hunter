# Runbook: Database Concurrency and Deadlock Prevention

## Objective
Ensure high-throughput background ingestion does not deadlock with API queries or interactive investigations.

## Locking Rules
1. Transactions must acquire table resources in consistent order:
   `scan_jobs` -> `platform_accounts` -> `relationship_edges` -> `account_features`.
2. Bulk insertions must use `BatchEdgeInserter` with chunk sizes <= 5,000 to minimize lock durations.
3. SQLite deployments must configure WAL mode (`PRAGMA journal_mode=WAL`) and `PRAGMA busy_timeout=5000`.
