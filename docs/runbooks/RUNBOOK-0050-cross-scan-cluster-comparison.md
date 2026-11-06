# Runbook 0050: Cross-Scan Cluster Comparison & Persistence Tracking

## Purpose
Track whether bot swarms persist or mutate across scheduled investigation scans.

## Procedure
1. Export Graph JSON bundle from Baseline Scan.
2. Export Graph JSON bundle from Follow-up Scan.
3. Compare `members` intersection across identified `cluster_id` records.
4. Flag accounts that survived initial quarantine wave for escalated review.
