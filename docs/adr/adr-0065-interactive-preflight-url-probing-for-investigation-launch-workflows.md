# ADR-0065: Interactive Preflight URL Probing for Investigation Launch Workflows

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Validate target account existence and inspect follower counts prior to provisioning scan jobs.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
