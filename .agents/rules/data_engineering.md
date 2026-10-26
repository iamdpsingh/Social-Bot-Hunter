# Data Engineering Rules

These rules govern all data pipelines, schemas, ingestion jobs, and persistence operations.

## Principles

1. **Clear Pipeline Contracts**: Every pipeline stage must explicitly define its:
   - Input format and source
   - Output destination and schema
   - Grain of records (e.g., one row per platform account observation per timestamp)
   - Failure and retry behaviour
2. **Idempotence by Design**: Every ingestion operation must be strictly idempotent. Re-running the same input with identical content hash must produce the exact same outcome without inserting duplicate records or inflating counts.
3. **Preserve Provenance**: Every external dataset and collected record must track source provenance, collection timestamps, and collection method (API, import, synthetic demo).
4. **Pre-Ingestion Validation**: Validate schemas, required fields, date formats, and value ranges before persistence or analytical use. Quarantine invalid records with explicit error reasons.
5. **No Synthetic Zeros**: Never silently convert missing, uncollected, or private fields into `0`. An unobserved count is `null` / `unavailable`, not zero.
6. **Versioned Definitions**: Explicitly version feature formulas (`feature_version`) and detection rule sets / models (`rules_version` / `model_version`). Never overwrite a historical version definition.
7. **Restartability & Checkpoints**: Ingestion must support resumable batching with transaction checkpoints. If an import fails midway, resume from the last committed checkpoint.
