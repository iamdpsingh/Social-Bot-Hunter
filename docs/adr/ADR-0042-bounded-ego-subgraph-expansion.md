# ADR-0042: Bounded Directional Ego-Subgraph Expansion Architecture

## Status
Accepted

## Context
Full social networks can contain millions of relationships. Analysts start investigations from a focal suspicious seed account and expand the graph incrementally.

## Decision
Implemented backend endpoint `/scans/{scan_id}/networks/nodes/{node_id}/neighbors` with radius bounded to 1 or 2 hops and directionality options (`in`, `out`, `both`), backed by `sbh.graph.ego.extract_ego_subgraph`.

## Consequences
- Prevents runaway query execution and memory spikes on super-connected influencer accounts.
- Provides interactive progressive disclosure in the UI.
