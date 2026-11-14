# ADR-0099: Micro-Benchmark Harness & Percentile Latency SLA

## Status
Accepted

## Context
System responsiveness requires strictly enforced latency bounds on hot-path operations (SQLite table lookups, SimHash hashing).

## Decision
Create `sbh.benchmarks` featuring `BenchmarkHarness` with configurable warmup iterations and percentile statistical aggregation (p50, p90, p95, p99). Enforce strict p99 SLAs: SQLite lookup &le; 5.0ms, SimHash hashing &le; 1.0ms.

## Consequences
Regressions in core data access or fingerprinting algorithms fail automated test gates before merge.
