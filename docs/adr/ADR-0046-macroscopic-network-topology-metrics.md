# ADR-0046: Macroscopic Network Topology Metrics Computation Model

## Status
Accepted

## Context
High-level bot detection requires macro-structural network measures: botnets exhibit abnormally low reciprocity, high clustering coefficients, and fragmented weakly connected components.

## Decision
Implemented `compute_graph_summary` in `sbh.graph.summary` computing node count, directed edge count, density, reciprocity, weakly connected components, strongly connected components, and average in/out degree.

## Consequences
- Immediate macro-topology overview via `GraphMetricsCard`.
- Fast NetworkX calculation with O(V + E) complexity.
