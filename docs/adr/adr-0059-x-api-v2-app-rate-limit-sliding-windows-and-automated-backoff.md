# ADR-0059: X API v2 App Rate Limit Sliding Windows and Automated Backoff

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Parse x-rate-limit-reset headers and raise structured RateLimitExceededError to prevent IP bans.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
