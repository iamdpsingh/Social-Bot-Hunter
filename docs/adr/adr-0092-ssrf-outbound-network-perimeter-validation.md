# ADR-0092: SSRF & Outbound Network Perimeter Validation

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Restricts outbound adapter HTTP calls by validating resolved IP addresses and denying link-local, loopback, private RFC 1918, and cloud metadata ranges.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
