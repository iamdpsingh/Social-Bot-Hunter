# Day 3: Database Locking Strategy

- SQLite WAL mode enabled on connection initialization.
- Busy timeout set to 5,000ms.
- Short transaction durations with chunked multi-row commits.
