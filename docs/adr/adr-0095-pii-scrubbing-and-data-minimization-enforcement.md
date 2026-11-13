# ADR-0095: PII Scrubbing & Data Minimization Enforcement

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Implements automated auditing of snapshot directories and export files to ensure un-fingerprinted personal data (emails, phones, IPs) never persists.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
