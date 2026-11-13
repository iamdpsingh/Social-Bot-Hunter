# ADR-0096: Security Audit Scorecard & Risk Grading Model

## Status
Accepted (Day 13 - 13 Nov 2026)

## Context
Defines the aggregate security scorecard formula evaluating secret presence, file permissions, environment variables, and dependency posture into an A-F letter grade.

## Decision
We enforce this architecture across Social Bot Hunter runtime, CLI, API, and background processes. All checks run locally offline without cloud telemetry or external network requirements.

## Consequences
- Zero credentials or PII leaked in local snapshots or exports.
- High-assurance offline verification compliant with enterprise privacy and security mandates.
- Full compatibility with air-gapped forensic workstations.
