# ADR-0010: High-Throughput Batch Edge Ingestion

## Status
Accepted

## Context
Social relationship graphs easily contain hundreds of thousands of directed edges. Inserting edges one-by-one results in excessive round-trips and transaction lock contention.

## Decision
Introduce `BatchEdgeInserter` implementing chunked multi-row parameter binding (default 2,000 rows/chunk) within isolated transactions. Uses `ON CONFLICT (scan_id, source, target, type) DO NOTHING` for deduplication.

## Consequences
- Achieves ingestion throughputs exceeding 10,000 edges/second on standard SSDs.
- Memory consumption remains strictly bounded regardless of overall dataset magnitude.
