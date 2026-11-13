# RUNBOOK-0096: SSRF Attack Forensics & Outbound Egress Lockdown

## Purpose
Incident triage for outbound URL fetch anomalies and metadata service access attempts.

## Scope
Applies to local investigators, automated CI runners, and platform administrators.

## Procedure
1. Execute `sbh audit-full --json` to capture baseline state.
2. Review findings table for category-specific violations.
3. Apply remediation steps documented in related ADRs.
4. Verify resolution with `sbh audit-secrets` and `pytest tests/security/`.
