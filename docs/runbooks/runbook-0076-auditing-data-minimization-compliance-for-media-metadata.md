# RUNBOOK-0076: Auditing Data Minimization Compliance for Media Metadata

## Summary
Verify that no raw binary media or private messages are persisted.

## Audit Query
`SELECT COUNT(*) FROM content WHERE raw_payload IS NOT NULL;`
Verify count equals 0.