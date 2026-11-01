# SQLite Compatibility and Concurrency

SQLite runs with `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, `PRAGMA foreign_keys=ON`, and `PRAGMA busy_timeout=5000` to prevent writer starvation.
