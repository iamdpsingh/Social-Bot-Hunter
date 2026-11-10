# RUNBOOK-0082: Triage and Remediation of Zip-Bomb Rejection Alerts

## Purpose
Diagnose why an uploaded dataset archive triggered the `ArchiveSecurityError` compression ratio ceiling.

## Steps
1. Inspect audit logs for `archive.upload` security violations.
2. Check compressed vs uncompressed size of submitted archive.
3. If legitimate large dataset, adjust `SBH_ARCHIVE_MAX_UNCOMPRESSED_MB` in configuration.
4. If compression ratio exceeds 100x, quarantine and advise analyst to repackage without excessive sparse zero-padding.
