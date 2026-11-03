# Runbook: Batch Ingestion Performance Tuning

## Objective
Optimize bulk relationship edge loading throughput according to database engine and storage hardware.

## Tuning Matrix
| Storage Backend | Disk Type | Recommended Chunk Size | Expected Throughput |
| :--- | :--- | :--- | :--- |
| SQLite (WAL) | NVMe / SSD | 2,000 rows | 12,000 edges/sec |
| PostgreSQL 16 | SSD / Cloud | 5,000 rows | 25,000 edges/sec |
| SQLite | HDD / Slow | 500 rows | 3,000 edges/sec |

Configure chunk size via `BatchEdgeInserter(db, chunk_size=N)`.
