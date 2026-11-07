# RUNBOOK-0055: Distinguishing Coverage Gaps from Proven Account Removals

## Purpose
Ensure operational reports never mislabel sampling gaps as confirmed account removals.

## Procedure
1. Verify if baseline scan collected full follower list (`completeness == 'complete'`).
2. If later scan was partial, missing accounts MUST be classified as `unobserved_gap`.
3. Consult `coverage-gap-banner` in dashboard for exact counts.
