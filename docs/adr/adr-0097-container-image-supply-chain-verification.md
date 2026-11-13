# ADR-0097: Container Image Supply Chain Verification

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Establishes standards for container provenance, explicit base image pinning, and Trivy static vulnerability scanning during release packaging.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
