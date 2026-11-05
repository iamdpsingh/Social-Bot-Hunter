# ADR 0031: Transparent Penalty Reductions for Unobservable Data

## Status
Accepted

## Context
Public platform APIs often restrict access to private messages, login IP history, and deleted posts. Treating missing data as benign leads to false negatives.

## Decision
Calculate an `evidence_coverage` ratio (0.0 to 1.0) and penalize confidence ratings when key indicator channels are unobservable. Disclose exact limitations via `LimitationsCard`.

## Consequences
- High scores with low coverage are flagged as tentative.
- Transparent reporting of data limitations in export bundles.
