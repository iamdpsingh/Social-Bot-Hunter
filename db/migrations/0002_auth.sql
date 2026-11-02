-- Social Bot Hunter: authentication and role-based access control schema.
-- Portable SQL subset accepted by both SQLite and PostgreSQL.

CREATE TABLE users (
    id              TEXT PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('admin', 'investigator', 'auditor', 'readonly')),
    full_name       TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_role ON users (role);

CREATE TABLE revoked_tokens (
    jti         TEXT PRIMARY KEY,
    token_type  TEXT NOT NULL CHECK (token_type IN ('access', 'refresh')),
    revoked_at  TIMESTAMPTZ NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_revoked_tokens_exp ON revoked_tokens (expires_at);
