# Dead-Letter Quarantine Engine

Records failing schema validation, constraint checks, or provenance requirements are routed to `quarantined_records` without failing the batch ingestion job.
