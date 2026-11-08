# ADR-0063: YouTube Subscriber Visibility and OAuth Scope Boundaries

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Distinguish public subscriptions from restricted subscriber enumeration with explicit AccessOutcome.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
