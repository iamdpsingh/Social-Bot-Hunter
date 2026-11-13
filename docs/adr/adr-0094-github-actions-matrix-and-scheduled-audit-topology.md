# ADR-0094: GitHub Actions Matrix & Scheduled Audit Topology

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Configures multi-version matrix testing across Python versions and scheduled recurring security vulnerability sweeps.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
