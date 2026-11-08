# ADR-0067: Cross-Platform Canonical Identity Synthesis and URL Rewriting

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Normalize twitter.com to x.com and @handles to canonical HTTPS URLs across all ingestion paths.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
