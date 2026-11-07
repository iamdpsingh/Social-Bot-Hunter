# RUNBOOK-0056: Data Retention Emergency Purge Procedure

## Purpose
Execute manual data purge for GDPR Right-to-be-Forgotten requests or storage quota relief.

## Procedure
1. Run dry run: `POST /api/v1/settings/retention/purge {"retention_days": 30, "dry_run": true}`.
2. Verify candidate count in response.
3. Execute live purge: `POST /api/v1/settings/retention/purge {"retention_days": 30, "dry_run": false}`.
4. Verify SQLite vacuum or page count reduction.
