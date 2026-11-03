# ADR-0012: Bounded Worker Concurrency and Queue Limits

## Status
Accepted

## Context
Unbounded concurrency causes severe resource starvation, SQLite lock timeouts (`database is locked`), and OS thread exhaustion.

## Decision
Configure `WorkerPool` with bounded worker concurrency (default 2 threads locally, configurable up to 16) and a bounded priority queue (default 200 tasks). Tasks exceeding queue capacity are rejected with HTTP 429.

## Consequences
- Prevents database connection pool exhaustion and memory bloat.
- Maintains low latency and high responsiveness for API queries during heavy scan ingestion.
