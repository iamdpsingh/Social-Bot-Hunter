# ADR-0052: Risk Score Migration Classification Across Multi-Scan Timelines

## Context
Accounts observed across multiple scans may evolve their behavior, becoming more automated or showing signs of human takeover.

## Decision
We compute risk delta score transitions (`score_after - score_before`) and classify changes into `escalated` (> +0.15), `deescalated` (< -0.15), or `stable`.

## Consequences
- Highlights accounts whose behavioral risk posture worsened between investigations.
