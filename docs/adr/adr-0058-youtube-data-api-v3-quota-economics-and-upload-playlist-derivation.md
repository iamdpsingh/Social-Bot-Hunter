# ADR-0058: YouTube Data API v3 Quota Economics and Upload Playlist Derivation

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Derived upload playlist (UU...) queries cut quota costs by 99% compared to search.list.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
