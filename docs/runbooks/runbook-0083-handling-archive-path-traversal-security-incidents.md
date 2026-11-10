# RUNBOOK-0083: Handling Archive Path Traversal Security Incidents

## Purpose
Respond to directory traversal attempts in dataset uploads.

## Steps
1. Identify the user account and IP address from the failed request audit entry.
2. Review the rejected member filename in logs.
3. Determine if weaponized payload or accidental packaging issue.
4. Retain rejected file in quarantined storage for security analysis.
