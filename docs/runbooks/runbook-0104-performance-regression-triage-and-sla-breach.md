# RUNBOOK-0104: Performance Regression Triage & SLA Breach

## Scope & Target
Investigating latency SLA breaches in query execution or SimHash fingerprinting.

## Operational Procedure
1. Execute micro-benchmark sweep: `python -m sbh benchmark --iterations 200`
2. Review p99 latency against SLAs:
   - `sqlite_in_memory_query`: SLA &le; 5.0 ms
   - `simhash_text_hashing`: SLA &le; 1.0 ms
3. If SLA fails:
   - Check SQLite index usage (`EXPLAIN QUERY PLAN`)
   - Check background process CPU contention
   - Run storage vacuum: `sqlite3 ./sbh-dev.sqlite "VACUUM;"`
