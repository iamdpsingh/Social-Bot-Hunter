# Data dictionary

All tables are created by `db/migrations/0001_init.sql`. The same SQL file is applied to SQLite
(tests, local development) and is intended for PostgreSQL. Identifiers are UUID strings stored as
`TEXT`; timestamps are `TIMESTAMPTZ` columns written as fixed-width UTC ISO-8601 strings; JSON
columns always hold an object or an array.

Two rules apply everywhere:

* **`NULL` means not observed.** Zero is a real observed zero. Features that cannot be computed are
  stored as unavailable with a reason, never as `0`.
* **Nothing is silently dropped.** Rejected input rows are kept in `quarantined_records` with reasons.

## Import format

A dataset is either a **directory** containing `manifest.json` plus any of `accounts.csv`,
`relationships.csv`, `content.csv`, or a single **JSON bundle**
`{"manifest": {...}, "accounts": [...], "relationships": [...], "content": [...]}`.
`python -m sbh generate-demo --out DIR` writes a complete example, and `data/samples/synthetic_demo/` is
a committed copy.

### `manifest.json`

| Field | Required | Notes |
|---|---|---|
| `schema_version` | yes | `1.x` accepted. A different major version is rejected. |
| `dataset_name` | yes | Used to flag unexpected row-count changes between imports. |
| `platform` | yes | One of `instagram`, `x`, `tiktok`, `youtube`, `linkedin`. One platform per dataset. |
| `collected_at` | yes | When the data was collected (ISO-8601 with timezone, not in the future). |
| `source_description` | yes | Provenance, in words. |
| `collection_method` | yes | `official_api_export`, `permitted_public_collection`, `third_party_dataset`, `synthetic`. |
| `relationship_coverage` | no | `{"default": "complete\|partial\|unknown", "overrides": [{"platform_account_id", "list_kind": "followers\|following", "completeness", "expected_count"}]}`. Defaults to `unknown`. |
| `notes` | no | Free text. |

`relationship_coverage` is how you say whether a followers/following list is the whole list. A scan
is only `complete` if every list is declared `complete`. A list declared `complete` with an
`expected_count` that does not match what was supplied is downgraded to `partial`.

### Row columns

| File | Required columns | Optional columns |
|---|---|---|
| `accounts.csv` | `platform`, `platform_account_id`, `observed_at` | `username`, `display_name`, `follower_count`, `following_count`, `post_count`, `has_bio`, `bio_length`, `has_profile_image`, `has_display_name`, `account_created_at`, `is_verified`, `is_private` |
| `relationships.csv` | `platform`, `source_account_id`, `target_account_id`, `relationship_type` (`follows`), `observed_at` | `verification_status` (`unverified`, `source_asserted`, `cross_checked`) |
| `content.csv` | `platform`, `platform_content_id`, `author_account_id`, `published_at` | `text`, `content_hash`, `like_count`, `reply_count`, `share_count` |

Rules: timestamps need an explicit timezone; counts are non-negative integers; booleans accept
`true/false/yes/no/1/0`; a blank cell is "not observed"; `source -> target` means *source follows
target* and the reverse is never inferred. `text`, if supplied, is turned into fingerprints and then
discarded. An unknown extra column is ignored with a warning; a missing required column rejects the
file.

## Tables

<!-- BEGIN GENERATED:data-dictionary -->
### `scan_jobs`

One investigation run: its mode, status, completeness and outcome detail.

- **Grain:** one row per scan
- **Retention:** Deleted with the scan (`sbh delete-scan`).

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_type` | TEXT | no |  |
| `collection_mode` | TEXT | no |  |
| `platform` | TEXT | no |  |
| `status` | TEXT | no | pending, running, complete, partial, failed, cancelled, awaiting_access_approval |
| `data_origin` | TEXT | no | synthetic, imported or api; synthetic scans are labelled as demo data everywhere |
| `requested_by` | TEXT | no |  |
| `created_at` | TIMESTAMPTZ | no |  |
| `started_at` | TIMESTAMPTZ | yes |  |
| `finished_at` | TIMESTAMPTZ | yes |  |
| `reference_time` | TIMESTAMPTZ | no | When the data was collected (manifest `collected_at`); used for freshness and reproducible re-analysis |
| `failure_reason` | TEXT | yes |  |
| `collection_completeness` | TEXT | yes | Are the observed relationship lists known to be whole? complete / partial / unknown |
| `config_version` | TEXT | yes |  |
| `config_sha256` | TEXT | yes |  |
| `status_detail` | JSONB | no | JSON: summary counts, partial reasons, data-quality warnings, graph stats |

### `dataset_imports`

Provenance of an imported dataset; its content hash makes imports idempotent.

- **Grain:** one row per imported input (unique content hash)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `dataset_name` | TEXT | no |  |
| `source_name` | TEXT | no |  |
| `content_sha256` | TEXT | no | unique; SHA-256 over the input bytes: the idempotency key |
| `schema_version` | TEXT | no |  |
| `collection_method` | TEXT | no |  |
| `source_description` | TEXT | no |  |
| `is_synthetic` | BOOLEAN | no |  |
| `manifest` | JSONB | no |  |
| `record_counts` | JSONB | no |  |
| `imported_at` | TIMESTAMPTZ | no |  |

### `scan_checkpoints`

Restart points: how far each write stage got.

- **Grain:** one row per (scan, stage)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `scan_id` | TEXT | no | primary key; FK -> scan_jobs.id |
| `stage` | TEXT | no | primary key |
| `cursor_pos` | INTEGER | no |  |
| `status` | TEXT | no |  |
| `updated_at` | TIMESTAMPTZ | no |  |

### `quarantined_records`

Rows rejected (or exact duplicates dropped) during validation, with reasons. Post text is never kept.

- **Grain:** one row per rejected input row
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `entity` | TEXT | no |  |
| `source_ref` | TEXT | no |  |
| `kind` | TEXT | no | invalid (rejected) or duplicate (exact duplicate, harmless) |
| `reasons` | JSONB | no |  |
| `raw` | JSONB | no |  |
| `created_at` | TIMESTAMPTZ | no |  |

### `platform_accounts`

Stable identity of an account on one platform. Usernames are mutable attributes, not identity.

- **Grain:** one row per (platform, platform_account_id)
- **Retention:** Removed when no remaining scan references the account.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `platform` | TEXT | no |  |
| `platform_account_id` | TEXT | no |  |
| `username` | TEXT | yes |  |
| `display_name` | TEXT | yes |  |
| `first_observed_at` | TIMESTAMPTZ | no |  |
| `last_observed_at` | TIMESTAMPTZ | no |  |
| `first_seen_scan_id` | TEXT | yes | FK -> scan_jobs.id; NULL after that scan is deleted |
| `metadata` | JSONB | no |  |
| `provenance` | TEXT | no |  |

### `account_observations`

What was observed about an account at a point in time. NULL means not observed; 0 is a real zero.

- **Grain:** one row per (account, scan, observed_at)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `platform_account_id` | TEXT | no | FK -> platform_accounts.id |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `observed_at` | TIMESTAMPTZ | no | When the platform state was observed (source time) |
| `collected_at` | TIMESTAMPTZ | no | When it was collected (scan reference time) |
| `username` | TEXT | yes |  |
| `display_name` | TEXT | yes |  |
| `follower_count` | BIGINT | yes |  |
| `following_count` | BIGINT | yes |  |
| `post_count` | BIGINT | yes |  |
| `has_bio` | BOOLEAN | yes |  |
| `bio_length` | INTEGER | yes |  |
| `has_profile_image` | BOOLEAN | yes |  |
| `has_display_name` | BOOLEAN | yes |  |
| `account_created_at` | TIMESTAMPTZ | yes | Only if the source supplied it; never inferred |
| `is_verified` | BOOLEAN | yes | Stored for context only; never used as proof of anything |
| `is_private` | BOOLEAN | yes |  |
| `source_payload_sha256` | TEXT | no | Hash of the raw input row (the row itself is not stored) |
| `provenance` | TEXT | no |  |

### `relationship_edges`

A directed 'source follows target' relationship observed by a scan. The reverse is never inferred.

- **Grain:** one row per (scan, source, target, type)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `platform` | TEXT | no |  |
| `source_account_id` | TEXT | no | FK -> platform_accounts.id |
| `target_account_id` | TEXT | no | FK -> platform_accounts.id |
| `relationship_type` | TEXT | no |  |
| `observed_at` | TIMESTAMPTZ | no |  |
| `collected_at` | TIMESTAMPTZ | no |  |
| `verification_status` | TEXT | no | unverified, source_asserted or cross_checked |
| `provenance` | TEXT | no |  |

### `relationship_list_coverage`

Whether an observed followers/following list is the complete list. Separates confirmed change from incomplete collection.

- **Grain:** one row per (scan, account, list kind)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `scan_id` | TEXT | no | primary key; FK -> scan_jobs.id |
| `platform_account_id` | TEXT | no | primary key; FK -> platform_accounts.id |
| `list_kind` | TEXT | no | primary key |
| `completeness` | TEXT | no |  |
| `observed_count` | INTEGER | no |  |
| `expected_count` | INTEGER | yes | Total the source claimed, if any; a mismatch downgrades 'complete' |

### `content_observations`

Post fingerprints and counts. Raw post text is never stored.

- **Grain:** one row per (scan, platform, content id)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `platform` | TEXT | no |  |
| `platform_content_id` | TEXT | no |  |
| `author_account_id` | TEXT | no | FK -> platform_accounts.id |
| `published_at` | TIMESTAMPTZ | no |  |
| `collected_at` | TIMESTAMPTZ | no |  |
| `content_hash` | TEXT | yes | SHA-256 of normalised text, or a source-supplied hash when no text was given |
| `simhash` | TEXT | yes | 64-bit near-duplicate fingerprint, 16 hex characters |
| `text_length` | INTEGER | yes |  |
| `like_count` | BIGINT | yes |  |
| `reply_count` | BIGINT | yes |  |
| `share_count` | BIGINT | yes |  |
| `provenance` | TEXT | no |  |

### `model_versions`

Immutable record of the rules/graph configuration that produced stored results.

- **Grain:** one row per (kind, name, version)
- **Retention:** Kept (configuration, not personal data).

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `kind` | TEXT | no |  |
| `name` | TEXT | no |  |
| `version` | TEXT | no |  |
| `config` | JSONB | no |  |
| `config_sha256` | TEXT | no | Reusing a version with different configuration is refused |
| `feature_schema` | JSONB | yes |  |
| `training_data_ref` | TEXT | yes |  |
| `evaluation` | JSONB | yes |  |
| `created_at` | TIMESTAMPTZ | no |  |

### `account_features`

Interpretable per-account signals. Unavailable features have no value and a reason.

- **Grain:** one row per (scan, account, feature, feature version)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `platform_account_id` | TEXT | no | FK -> platform_accounts.id |
| `feature_name` | TEXT | no |  |
| `feature_version` | TEXT | no |  |
| `category` | TEXT | no |  |
| `value` | DOUBLE PRECISION | yes | NULL iff the feature is unavailable (enforced by a CHECK constraint) |
| `is_available` | BOOLEAN | no |  |
| `unavailable_reason` | TEXT | yes |  |
| `details` | JSONB | no |  |
| `computed_at` | TIMESTAMPTZ | no |  |

### `risk_assessments`

Explainable heuristic risk result, or an insufficient-evidence result with no score.

- **Grain:** one row per (scan, account, model version, feature version)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `platform_account_id` | TEXT | no | FK -> platform_accounts.id |
| `feature_version` | TEXT | no |  |
| `model_version_id` | TEXT | no | FK -> model_versions.id |
| `status` | TEXT | no |  |
| `score` | DOUBLE PRECISION | yes | 0-100 heuristic indicator, NULL when evidence is insufficient (CHECK-enforced) |
| `band` | TEXT | yes |  |
| `evidence_coverage` | DOUBLE PRECISION | no | Available rule weight divided by total rule weight |
| `features_available` | INTEGER | no |  |
| `features_total` | INTEGER | no |  |
| `contributions` | JSONB | no | JSON: every rule with value, evidence, weight and score points, or why unavailable |
| `limitations` | JSONB | no |  |
| `assessed_at` | TIMESTAMPTZ | no |  |

### `network_clusters`

A candidate group of accounts with signals, coverage, uncertainty and alternative explanations.

- **Grain:** one row per detected cluster per scan
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `model_version_id` | TEXT | no | FK -> model_versions.id |
| `method` | TEXT | no |  |
| `method_version` | TEXT | no |  |
| `member_count` | INTEGER | no |  |
| `metrics` | JSONB | no |  |
| `signals` | JSONB | no |  |
| `coverage` | JSONB | no |  |
| `signal_strength` | TEXT | no | low = structure only; moderate/high = one/two or more independent behavioural signals |
| `confidence` | TEXT | no | Capped by data coverage; automation never sets 'high' |
| `uncertainty_notes` | JSONB | no |  |
| `alternative_explanations` | JSONB | no |  |
| `review_status` | TEXT | no | Human review state; starts as unreviewed |
| `reviewed_by` | TEXT | yes |  |
| `reviewed_at` | TIMESTAMPTZ | yes |  |
| `created_at` | TIMESTAMPTZ | no |  |

### `cluster_memberships`

Which accounts belong to which candidate cluster, with member-level metrics.

- **Grain:** one row per (cluster, account)
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `cluster_id` | TEXT | no | primary key; FK -> network_clusters.id |
| `platform_account_id` | TEXT | no | primary key; FK -> platform_accounts.id |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `metrics` | JSONB | no |  |

### `evidence_records`

Human-readable evidence behind a score or cluster, with references to source rows.

- **Grain:** one row per piece of evidence
- **Retention:** Deleted with the scan.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `scan_id` | TEXT | no | FK -> scan_jobs.id |
| `subject_type` | TEXT | no |  |
| `subject_id` | TEXT | no | platform_accounts.id or network_clusters.id depending on subject_type (no FK: polymorphic) |
| `evidence_type` | TEXT | no |  |
| `summary` | TEXT | no |  |
| `details` | JSONB | no |  |
| `source_refs` | JSONB | no |  |
| `model_version_id` | TEXT | no | FK -> model_versions.id |
| `created_at` | TIMESTAMPTZ | no |  |

### `platform_capabilities`

Persisted capability registry: what each platform operation supports and how far that is verified.

- **Grain:** one row per (platform, operation)
- **Retention:** Kept (configuration).

| Column | Type | Null | Notes |
|---|---|---|---|
| `platform` | TEXT | no | primary key |
| `operation` | TEXT | no | primary key |
| `collection_mode` | TEXT | no |  |
| `status` | TEXT | no | implemented, verified, requires_approval, unsupported, temporarily_unavailable, not_configured |
| `supported` | BOOLEAN | yes | NULL = not yet established from official documentation |
| `endpoint` | TEXT | yes |  |
| `api_version` | TEXT | yes |  |
| `required_scopes` | JSONB | no |  |
| `requires_approval` | BOOLEAN | yes |  |
| `pagination_notes` | TEXT | yes |  |
| `quota_notes` | TEXT | yes |  |
| `credentials_required` | JSONB | no |  |
| `retention_notes` | TEXT | yes |  |
| `limitations` | JSONB | no |  |
| `last_verified_at` | TIMESTAMPTZ | yes |  |
| `verification_evidence` | TEXT | yes |  |
| `updated_at` | TIMESTAMPTZ | no |  |

### `audit_events`

Security-relevant actions: scan lifecycle, rejected imports, deletions.

- **Grain:** one row per event
- **Retention:** Kept; contains no deleted content.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | TEXT | no | primary key |
| `occurred_at` | TIMESTAMPTZ | no |  |
| `actor` | TEXT | no | 'cli' or a service name today; user ids once authentication exists |
| `action` | TEXT | no |  |
| `subject_type` | TEXT | no |  |
| `subject_id` | TEXT | yes |  |
| `details` | JSONB | no |  |
<!-- END GENERATED:data-dictionary -->

## Provenance

Every account, observation, edge and content row carries a `provenance` string of the form
`dataset_import:<dataset_name>:<first 12 hex of the input hash>`, and the owning scan links to
`dataset_imports`, which keeps the manifest. Derived rows (`account_features`, `risk_assessments`,
`network_clusters`, `evidence_records`) reference their scan, and assessments and clusters also
reference the `model_versions` row that produced them.
