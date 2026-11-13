# ADR-0091: Hardened Multi-Stage Docker & Non-Root Execution

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Mandates explicit non-root user creation (UID 10001 / 1001), healthchecks, and multi-stage builds eliminating build compilers from final images.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
