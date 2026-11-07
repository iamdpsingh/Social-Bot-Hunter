# RUNBOOK-0051: SimHash Content Clustering Calibration

## Purpose
Guide for adjusting Hamming distance thresholds in SimHash near-duplicate clustering.

## Procedure
1. Inspect message lengths: for short messages (<15 words), use threshold <= 8 bits.
2. For long forum posts (>100 words), adjust threshold up to 12 bits.
3. Verify cluster cohesion using `/api/v1/scans/{scan_id}/coordination?min_similarity_distance={val}`.
