# ADR-0064: Replay Fixture Architecture for Deterministic Offline Adapter Testing

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Offline recorded JSON fixtures guarantee 100% cloud-free local unit test execution.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
