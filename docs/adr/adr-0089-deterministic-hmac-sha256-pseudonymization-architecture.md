# ADR-0089: Deterministic HMAC-SHA256 Pseudonymization Architecture

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Adopts keyed HMAC-SHA256 hashing for social network entity identifiers to ensure irreversible privacy preservation while maintaining graph topology comparability.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
