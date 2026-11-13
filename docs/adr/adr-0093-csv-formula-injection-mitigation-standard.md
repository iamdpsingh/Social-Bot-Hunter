# ADR-0093: CSV & Spreadsheet Formula Injection Mitigation Standard

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Guarantees that all user-supplied content in CSV/spreadsheet exports starting with formula trigger characters (=, +, -, @, tab, cr) is escaped with a leading single quote.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
