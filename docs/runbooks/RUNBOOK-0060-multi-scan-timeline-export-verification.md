# RUNBOOK-0060: Multi-Scan Timeline Export Verification

## Purpose
Verify integrity of longitudinal investigation diff exports for legal and audit compliance.

## Procedure
1. Export scan diff bundle using `/api/v1/diff`.
2. Verify provenance notes and checksum hashes.
3. Archive export artifact in `data/exports/diff_{scanA}_{scanB}.json`.
