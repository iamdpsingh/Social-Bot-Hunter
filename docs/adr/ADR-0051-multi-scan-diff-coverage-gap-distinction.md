# ADR-0051: Semantic Separation Between Confirmed Removals and Unobserved Coverage Gaps

## Context
When comparing investigation scans taken at different times, accounts missing in later scans may simply be unobserved due to sampling limits rather than deleted or banned.

## Decision
We strictly enforce a semantic division:
1. `confirmed_removed`: absent later, but later collection coverage was proven complete.
2. `coverage_gap` (unobserved): absent later, but later collection was incomplete or depth-limited.

## Consequences
- Analysts are never misled into concluding bot networks were disbanded when collection coverage was simply partial.
