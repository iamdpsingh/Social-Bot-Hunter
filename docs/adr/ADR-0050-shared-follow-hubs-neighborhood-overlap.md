# ADR-0050: Inverted Index Neighborhood Jaccard Overlap for Shared Follow Hubs

## Context
Coordinated inauthentic networks often share common target destinations (amplification targets or shared follow hubs). Comparing all N^2 pairs in large graphs is computationally prohibitive.

## Decision
We utilize an inverted index mapping target nodes to followers, pruning candidate generation past high-degree celebrity thresholds, and compute Jaccard neighborhood overlaps.

## Consequences
- Sub-quadratic scaling over sparse social networks.
- Pinpoints coordinated follow targets without performance degradation.
