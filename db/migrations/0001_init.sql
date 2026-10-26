-- Social Bot Hunter: initial schema.
--
-- Written in a SQL subset that both PostgreSQL and SQLite accept, so the file executed by the
-- test-suite (SQLite) is byte-for-byte the file intended for PostgreSQL / Cloud SQL.
-- Conventions:
--   * ids are UUID strings stored as TEXT (portable, no driver-specific uuid handling);
--   * timestamps are TIMESTAMPTZ columns written as fixed-width UTC ISO-8601 strings;
--   * JSONB columns always hold a JSON object or array (never a bare scalar);
--   * "NULL means not observed"; zero is a real observed value.
-- See docs/data-dictionary.md for the grain and meaning of every table.

CREATE TABLE scan_jobs (
    id                      TEXT PRIMARY KEY,
    scan_type               TEXT NOT NULL CHECK (scan_type IN ('dataset_import', 'api_collection')),
    collection_mode         TEXT NOT NULL CHECK (collection_mode IN ('official_api', 'dataset_import', 'public_data')),
    platform                TEXT NOT NULL CHECK (platform IN ('instagram', 'x', 'tiktok', 'youtube', 'linkedin')),
    status                  TEXT NOT NULL CHECK (status IN ('pending', 'running', 'complete', 'partial', 'failed', 'cancelled', 'awaiting_access_approval')),
    data_origin             TEXT NOT NULL CHECK (data_origin IN ('synthetic', 'imported', 'api')),
    requested_by            TEXT NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL,
    started_at              TIMESTAMPTZ,
    finished_at             TIMESTAMPTZ,
    reference_time          TIMESTAMPTZ NOT NULL,
    failure_reason          TEXT,
    collection_completeness TEXT CHECK (collection_completeness IN ('complete', 'partial', 'unknown')),
    config_version          TEXT,
    config_sha256           TEXT,
    status_detail           JSONB NOT NULL
);
CREATE INDEX idx_scan_jobs_status ON scan_jobs (status, created_at);

CREATE TABLE dataset_imports (
    id                TEXT PRIMARY KEY,
    scan_id           TEXT NOT NULL REFERENCES scan_jobs (id),
    dataset_name      TEXT NOT NULL,
    source_name       TEXT NOT NULL,
    content_sha256    TEXT NOT NULL UNIQUE,
    schema_version    TEXT NOT NULL,
    collection_method TEXT NOT NULL,
    source_description TEXT NOT NULL,
    is_synthetic      BOOLEAN NOT NULL,
    manifest          JSONB NOT NULL,
    record_counts     JSONB NOT NULL,
    imported_at       TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_dataset_imports_name ON dataset_imports (dataset_name, imported_at);

CREATE TABLE scan_checkpoints (
    scan_id    TEXT NOT NULL REFERENCES scan_jobs (id),
    stage      TEXT NOT NULL,
    cursor_pos INTEGER NOT NULL CHECK (cursor_pos >= 0),
    status     TEXT NOT NULL CHECK (status IN ('in_progress', 'done')),
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (scan_id, stage)
);

CREATE TABLE quarantined_records (
    id         TEXT PRIMARY KEY,
    scan_id    TEXT NOT NULL REFERENCES scan_jobs (id),
    entity     TEXT NOT NULL CHECK (entity IN ('account', 'relationship', 'content')),
    source_ref TEXT NOT NULL,
    kind       TEXT NOT NULL CHECK (kind IN ('invalid', 'duplicate')),
    reasons    JSONB NOT NULL,
    raw        JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    UNIQUE (scan_id, entity, source_ref)
);

CREATE TABLE platform_accounts (
    id                  TEXT PRIMARY KEY,
    platform            TEXT NOT NULL CHECK (platform IN ('instagram', 'x', 'tiktok', 'youtube', 'linkedin')),
    platform_account_id TEXT NOT NULL,
    username            TEXT,
    display_name        TEXT,
    first_observed_at   TIMESTAMPTZ NOT NULL,
    last_observed_at    TIMESTAMPTZ NOT NULL,
    first_seen_scan_id  TEXT REFERENCES scan_jobs (id) ON DELETE SET NULL,  -- NULL once that scan is deleted
    metadata            JSONB NOT NULL,
    provenance          TEXT NOT NULL,
    UNIQUE (platform, platform_account_id)
);

CREATE TABLE account_observations (
    id                   TEXT PRIMARY KEY,
    platform_account_id  TEXT NOT NULL REFERENCES platform_accounts (id),
    scan_id              TEXT NOT NULL REFERENCES scan_jobs (id),
    observed_at          TIMESTAMPTZ NOT NULL,
    collected_at         TIMESTAMPTZ NOT NULL,
    username             TEXT,
    display_name         TEXT,
    follower_count       BIGINT CHECK (follower_count IS NULL OR follower_count >= 0),
    following_count      BIGINT CHECK (following_count IS NULL OR following_count >= 0),
    post_count           BIGINT CHECK (post_count IS NULL OR post_count >= 0),
    has_bio              BOOLEAN,
    bio_length           INTEGER CHECK (bio_length IS NULL OR bio_length >= 0),
    has_profile_image    BOOLEAN,
    has_display_name     BOOLEAN,
    account_created_at   TIMESTAMPTZ,
    is_verified          BOOLEAN,
    is_private           BOOLEAN,
    source_payload_sha256 TEXT NOT NULL,
    provenance           TEXT NOT NULL,
    UNIQUE (platform_account_id, scan_id, observed_at)
);
CREATE INDEX idx_account_obs_account ON account_observations (platform_account_id, observed_at);
CREATE INDEX idx_account_obs_scan ON account_observations (scan_id);

-- Grain: one row per (scan, source, target, type): "this scan observed source -> target".
-- Directed. The reverse edge is never inferred.
CREATE TABLE relationship_edges (
    id                  TEXT PRIMARY KEY,
    scan_id             TEXT NOT NULL REFERENCES scan_jobs (id),
    platform            TEXT NOT NULL CHECK (platform IN ('instagram', 'x', 'tiktok', 'youtube', 'linkedin')),
    source_account_id   TEXT NOT NULL REFERENCES platform_accounts (id),
    target_account_id   TEXT NOT NULL REFERENCES platform_accounts (id),
    relationship_type   TEXT NOT NULL CHECK (relationship_type IN ('follows')),
    observed_at         TIMESTAMPTZ NOT NULL,
    collected_at        TIMESTAMPTZ NOT NULL,
    verification_status TEXT NOT NULL CHECK (verification_status IN ('unverified', 'source_asserted', 'cross_checked')),
    provenance          TEXT NOT NULL,
    CHECK (source_account_id <> target_account_id),
    UNIQUE (scan_id, source_account_id, target_account_id, relationship_type)
);
CREATE INDEX idx_edges_scan_source ON relationship_edges (scan_id, source_account_id);
CREATE INDEX idx_edges_scan_target ON relationship_edges (scan_id, target_account_id);

-- Grain: one row per (scan, subject account, list kind). Records whether the observed
-- followers/following list is the whole list. This is what separates a confirmed removal
-- from an incomplete collection when two scans are compared.
CREATE TABLE relationship_list_coverage (
    scan_id             TEXT NOT NULL REFERENCES scan_jobs (id),
    platform_account_id TEXT NOT NULL REFERENCES platform_accounts (id),
    list_kind           TEXT NOT NULL CHECK (list_kind IN ('followers', 'following')),
    completeness        TEXT NOT NULL CHECK (completeness IN ('complete', 'partial', 'unknown')),
    observed_count      INTEGER NOT NULL CHECK (observed_count >= 0),
    expected_count      INTEGER CHECK (expected_count IS NULL OR expected_count >= 0),
    PRIMARY KEY (scan_id, platform_account_id, list_kind)
);

-- Raw post text is never stored; only fingerprints and counts.
CREATE TABLE content_observations (
    id                   TEXT PRIMARY KEY,
    scan_id              TEXT NOT NULL REFERENCES scan_jobs (id),
    platform             TEXT NOT NULL CHECK (platform IN ('instagram', 'x', 'tiktok', 'youtube', 'linkedin')),
    platform_content_id  TEXT NOT NULL,
    author_account_id    TEXT NOT NULL REFERENCES platform_accounts (id),
    published_at         TIMESTAMPTZ NOT NULL,
    collected_at         TIMESTAMPTZ NOT NULL,
    content_hash         TEXT,
    simhash              TEXT,
    text_length          INTEGER CHECK (text_length IS NULL OR text_length >= 0),
    like_count           BIGINT CHECK (like_count IS NULL OR like_count >= 0),
    reply_count          BIGINT CHECK (reply_count IS NULL OR reply_count >= 0),
    share_count          BIGINT CHECK (share_count IS NULL OR share_count >= 0),
    provenance           TEXT NOT NULL,
    UNIQUE (scan_id, platform, platform_content_id)
);
CREATE INDEX idx_content_scan_author ON content_observations (scan_id, author_account_id, published_at);
CREATE INDEX idx_content_scan_hash ON content_observations (scan_id, content_hash);

CREATE TABLE model_versions (
    id                TEXT PRIMARY KEY,
    kind              TEXT NOT NULL CHECK (kind IN ('rules', 'ml', 'graph')),
    name              TEXT NOT NULL,
    version           TEXT NOT NULL,
    config            JSONB NOT NULL,
    config_sha256     TEXT NOT NULL,
    feature_schema    JSONB,
    training_data_ref TEXT,
    evaluation        JSONB,
    created_at        TIMESTAMPTZ NOT NULL,
    UNIQUE (kind, name, version)
);

CREATE TABLE account_features (
    id                  TEXT PRIMARY KEY,
    scan_id             TEXT NOT NULL REFERENCES scan_jobs (id),
    platform_account_id TEXT NOT NULL REFERENCES platform_accounts (id),
    feature_name        TEXT NOT NULL,
    feature_version     TEXT NOT NULL,
    category            TEXT NOT NULL CHECK (category IN ('profile', 'behavioural', 'network', 'data_quality')),
    value               DOUBLE PRECISION,
    is_available        BOOLEAN NOT NULL,
    unavailable_reason  TEXT,
    details             JSONB NOT NULL,
    computed_at         TIMESTAMPTZ NOT NULL,
    -- Missing is not zero: an unavailable feature has no value, an available one must have one.
    CHECK ((is_available = TRUE AND value IS NOT NULL) OR (is_available = FALSE AND value IS NULL)),
    UNIQUE (scan_id, platform_account_id, feature_name, feature_version)
);
CREATE INDEX idx_features_scan ON account_features (scan_id, feature_version);

CREATE TABLE risk_assessments (
    id                  TEXT PRIMARY KEY,
    scan_id             TEXT NOT NULL REFERENCES scan_jobs (id),
    platform_account_id TEXT NOT NULL REFERENCES platform_accounts (id),
    feature_version     TEXT NOT NULL,
    model_version_id    TEXT NOT NULL REFERENCES model_versions (id),
    status              TEXT NOT NULL CHECK (status IN ('scored', 'insufficient_evidence')),
    score               DOUBLE PRECISION CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
    band                TEXT,
    evidence_coverage   DOUBLE PRECISION NOT NULL CHECK (evidence_coverage >= 0 AND evidence_coverage <= 1),
    features_available  INTEGER NOT NULL CHECK (features_available >= 0),
    features_total      INTEGER NOT NULL CHECK (features_total >= 0),
    contributions       JSONB NOT NULL,
    limitations         JSONB NOT NULL,
    assessed_at         TIMESTAMPTZ NOT NULL,
    CHECK ((status = 'scored' AND score IS NOT NULL AND band IS NOT NULL)
        OR (status = 'insufficient_evidence' AND score IS NULL AND band IS NULL)),
    UNIQUE (scan_id, platform_account_id, model_version_id, feature_version)
);
CREATE INDEX idx_assessments_scan ON risk_assessments (scan_id, status);

CREATE TABLE network_clusters (
    id                       TEXT PRIMARY KEY,
    scan_id                  TEXT NOT NULL REFERENCES scan_jobs (id),
    model_version_id         TEXT NOT NULL REFERENCES model_versions (id),
    method                   TEXT NOT NULL,
    method_version           TEXT NOT NULL,
    member_count             INTEGER NOT NULL CHECK (member_count >= 2),
    metrics                  JSONB NOT NULL,
    signals                  JSONB NOT NULL,
    coverage                 JSONB NOT NULL,
    signal_strength          TEXT NOT NULL CHECK (signal_strength IN ('low', 'moderate', 'high')),
    confidence               TEXT NOT NULL CHECK (confidence IN ('low', 'moderate', 'high')),
    uncertainty_notes        JSONB NOT NULL,
    alternative_explanations JSONB NOT NULL,
    review_status            TEXT NOT NULL CHECK (review_status IN ('unreviewed', 'confirmed_coordinated', 'dismissed', 'needs_more_data')),
    reviewed_by              TEXT,
    reviewed_at              TIMESTAMPTZ,
    created_at               TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_clusters_scan ON network_clusters (scan_id);

CREATE TABLE cluster_memberships (
    cluster_id          TEXT NOT NULL REFERENCES network_clusters (id),
    platform_account_id TEXT NOT NULL REFERENCES platform_accounts (id),
    scan_id             TEXT NOT NULL REFERENCES scan_jobs (id),
    metrics             JSONB NOT NULL,
    PRIMARY KEY (cluster_id, platform_account_id)
);
CREATE INDEX idx_memberships_account ON cluster_memberships (platform_account_id, scan_id);

-- subject_id is polymorphic (platform_accounts.id or network_clusters.id), so it carries no
-- foreign key; the application guarantees it and tests assert it.
CREATE TABLE evidence_records (
    id               TEXT PRIMARY KEY,
    scan_id          TEXT NOT NULL REFERENCES scan_jobs (id),
    subject_type     TEXT NOT NULL CHECK (subject_type IN ('account', 'cluster')),
    subject_id       TEXT NOT NULL,
    evidence_type    TEXT NOT NULL,
    summary          TEXT NOT NULL,
    details          JSONB NOT NULL,
    source_refs      JSONB NOT NULL,
    model_version_id TEXT NOT NULL REFERENCES model_versions (id),
    created_at       TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_evidence_subject ON evidence_records (scan_id, subject_type, subject_id);

CREATE TABLE platform_capabilities (
    platform              TEXT NOT NULL CHECK (platform IN ('instagram', 'x', 'tiktok', 'youtube', 'linkedin')),
    operation             TEXT NOT NULL,
    collection_mode       TEXT NOT NULL CHECK (collection_mode IN ('official_api', 'dataset_import', 'public_data')),
    status                TEXT NOT NULL CHECK (status IN ('implemented', 'verified', 'requires_approval', 'unsupported', 'temporarily_unavailable', 'not_configured')),
    supported             BOOLEAN,
    endpoint              TEXT,
    api_version           TEXT,
    required_scopes       JSONB NOT NULL,
    requires_approval     BOOLEAN,
    pagination_notes      TEXT,
    quota_notes           TEXT,
    credentials_required  JSONB NOT NULL,
    retention_notes       TEXT,
    limitations           JSONB NOT NULL,
    last_verified_at      TIMESTAMPTZ,
    verification_evidence TEXT,
    updated_at            TIMESTAMPTZ NOT NULL,
    CHECK (status <> 'verified' OR (last_verified_at IS NOT NULL AND verification_evidence IS NOT NULL)),
    PRIMARY KEY (platform, operation)
);

CREATE TABLE audit_events (
    id           TEXT PRIMARY KEY,
    occurred_at  TIMESTAMPTZ NOT NULL,
    actor        TEXT NOT NULL,
    action       TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id   TEXT,
    details      JSONB NOT NULL
);
CREATE INDEX idx_audit_time ON audit_events (occurred_at);
CREATE INDEX idx_audit_subject ON audit_events (subject_type, subject_id);
