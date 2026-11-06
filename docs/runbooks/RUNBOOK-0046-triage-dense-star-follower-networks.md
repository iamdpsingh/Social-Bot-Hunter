# Runbook 0046: Triage Dense Star-Follower Astroturfing Campaigns

## Objective
Detect artificial follower pumps directed at target public figures.

## Indicators
- High In-Degree Centrality on single node with Low Out-Degree (Authority node).
- Hundreds of inbound edges from newly created, high-risk accounts.
- Graph reciprocity near 0.0%.

## Action
1. Filter by `Risk Band: Critical`.
2. Observe if arrows converge on a single victim/beneficiary account.
3. Bulk tag all inbound leaf nodes for quarantine review.
