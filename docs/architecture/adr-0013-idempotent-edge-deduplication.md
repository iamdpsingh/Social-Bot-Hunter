# ADR-0013: Idempotent Relationship Edge Deduplication

## Status
Accepted

## Context
Social networks frequently return duplicate follower entries across paginated queries or repeated scans.

## Decision
Enforce a composite uniqueness constraint on `(scan_id, source_account_id, target_account_id, relationship_type)`. All bulk edge insertions employ `ON CONFLICT ... DO NOTHING`.

## Consequences
- Guaranteed graph topology integrity without duplicated edges or inflated degrees.
- Eliminates the need for pre-insertion memory deduplication passes.
