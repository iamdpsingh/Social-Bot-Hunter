# Day 3: Failure Modes Analysis

Analyzed failure modes:
1. Process termination -> Checkpoint recovery.
2. External API 429 -> Exponential backoff.
3. Corrupted input batch -> Quarantine staging.
4. Client disconnect -> SSE graceful cleanup.
