# ADR 0033: 1-Hop Account Neighborhood Subgraph Inspection

## Status
Accepted

## Context
Analysts inspecting a flagged bot account need immediate visibility into who follows it and who it follows within the scanned investigation universe.

## Decision
Expose `AccountNeighborhoodViewer` rendering incoming and outgoing 1-hop edges with distinct direction badges and truncated identifiers.

## Consequences
- Rapid identification of anchor nodes and follower farm clusters.
- Low-latency local subgraph lookups without full graph traversals.
