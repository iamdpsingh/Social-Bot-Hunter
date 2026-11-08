# ADR-0061: Unified Record Schema Across Official Live APIs and Static Datasets

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Use immutable AccountObservationRecord, RelationshipRecord, and ContentRecord across all origins.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
