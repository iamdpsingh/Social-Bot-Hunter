# ADR-0062: In-Memory and Persistent Quota Ledgers with Midnight UTC Boundary Resets

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Enforce strict ceiling checks on third-party quotas to prevent unexpected billing overruns.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
