# Runbook 0040: Triage of False-Positive Risk Scoring Reports

## Objective
Investigate reports where authentic human accounts received critical risk ratings.

## Triage Actions
1. Navigate to `/investigations/[id]/accounts/[accountId]`.
2. Inspect `EvidenceInspector` to see which heuristic rule contributed disproportionate weight.
3. If rule is overly sensitive, adjust rule weight threshold in rule configuration.
