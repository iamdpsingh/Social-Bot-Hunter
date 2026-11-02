-- Social Bot Hunter: rollback script for 0002_auth.sql
-- Portable SQL subset accepted by both SQLite and PostgreSQL.

DROP TABLE IF EXISTS revoked_tokens;
DROP TABLE IF EXISTS users;
