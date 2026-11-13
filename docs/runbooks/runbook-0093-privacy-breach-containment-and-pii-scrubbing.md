# RUNBOOK-0093: Privacy Breach Containment & PII Scrubbing

## Purpose
Emergency sanitization runbook to purge unhashed personal identifiers from storage tables and caches.

## Scope
Applies to local investigators, automated CI runners, and platform administrators.

## Procedure
1. Execute `sbh audit-full --json` to capture baseline state.
2. Review findings table for category-specific violations.
3. Apply remediation steps documented in related ADRs.
4. Verify resolution with `sbh audit-secrets` and `pytest tests/security/`.
