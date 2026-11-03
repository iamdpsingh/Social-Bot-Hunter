# ADR-0016: Optimistic Locking State Machine Transitions

## Status
Accepted

## Context
Concurrent worker processes or simultaneous user cancellation requests can lead to race conditions during scan state transitions.

## Decision
Enforce atomic transitions via SQL `UPDATE scan_jobs SET status = :target WHERE id = :id AND status IN (...)`. The transition only succeeds if rowcount equals 1; otherwise, `InvalidTransitionError` is raised.

## Consequences
- Strictly prevents illegal transitions (e.g. `complete` -> `running`).
- Guarantees deterministic state changes under high concurrency.
