# Day 3: Scan State Machine Specification

Defined formal lifecycle transitions:
- `pending` -> `running`, `cancelled`, `failed`
- `running` -> `complete`, `partial`, `failed`, `cancelled`
- `failed` -> `pending` (via retry)
- `cancelled` -> `pending` (via retry)

All transitions execute atomically against persistent storage with optimistic concurrency checks.
