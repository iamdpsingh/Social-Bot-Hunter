# ADR-0088: Automated Secret Detection & Entropy Thresholding

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Enforces regex scanning coupled with Shannon entropy calculations to detect API tokens, keys, and credentials without false positives on placeholder strings.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
