# RUNBOOK-0054: Investigating Scan Diff Anomalies

## Purpose
Triage unexpected spikes in account additions or removals between two scans.

## Procedure
1. Navigate to `/history/diff?scan_a={baseline}&scan_b={comparison}`.
2. Inspect `Confirmed Additions` vs `Coverage Gaps`.
3. Filter by `persisting` to review escalated risk scores.
