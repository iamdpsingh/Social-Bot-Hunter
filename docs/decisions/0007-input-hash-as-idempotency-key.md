# ADR-0007: The input's SHA-256 is the idempotency key

**Status:** accepted

**Decision.** `dataset_imports.content_sha256` is unique. Importing the same bytes returns the stored
result. A `failed` scan for the same bytes is resumed from checkpoints; a `running` one is refused
unless an operator forces it; a `cancelled` one cannot be resumed. Row inserts also use
`ON CONFLICT DO NOTHING`, and each write batch commits with its checkpoint.

**Consequences.** Exactly-once effects without a job queue. A semantically identical file with
different bytes (re-serialised JSON) is a new scan: this is intentional, since the provenance differs.
The uniqueness is global, which assumes a single tenant; revisit it with multi-user access. Deleting a
scan frees its hash.
