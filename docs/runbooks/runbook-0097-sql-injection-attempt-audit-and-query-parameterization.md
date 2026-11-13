# RUNBOOK-0097: SQL Injection Attempt Audit & Parameterization

## Purpose
Review procedures for audit logs showing syntax anomalies in search filters or raw queries.

## Scope
Applies to local investigators, automated CI runners, and platform administrators.

## Procedure
1. Execute `sbh audit-full --json` to capture baseline state.
2. Review findings table for category-specific violations.
3. Apply remediation steps documented in related ADRs.
4. Verify resolution with `sbh audit-secrets` and `pytest tests/security/`.
