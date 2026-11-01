# Connection Pooling Specification

PostgreSQL uses `psycopg_pool.ConnectionPool` with configurable min/max sizing, timeout thresholds, and health checks. Pool exhaustion raises `PoolTimeout` errors.
