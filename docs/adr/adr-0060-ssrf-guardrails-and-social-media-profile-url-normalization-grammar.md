# ADR-0060: SSRF Guardrails and Social Media Profile URL Normalization Grammar

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Enforce strict scheme whitelists, RFC1918 private range blocks, and canonical profile rewriting.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
