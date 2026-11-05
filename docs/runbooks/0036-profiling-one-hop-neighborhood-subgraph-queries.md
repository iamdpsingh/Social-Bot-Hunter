# Runbook 0036: Profiling 1-Hop Neighborhood Subgraph Queries

## Objective
Optimize query execution times for `list_relationship_edges` during heavy follower analysis.

## Tuning Actions
1. Confirm index on `(scan_id, source_id)` and `(scan_id, target_id)`.
2. Run `EXPLAIN QUERY PLAN SELECT * FROM relationship_edges WHERE scan_id = ? AND source_id = ?`.
3. Verify query scans index rather than performing full table scans.
