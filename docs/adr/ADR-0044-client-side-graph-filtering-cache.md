# ADR-0044: Client-Side Graph Filtering and Search Cache Architecture

## Status
Accepted

## Context
Users expect real-time feedback when typing account usernames or sliding risk score threshold bars without waiting for network round-trips.

## Decision
Implemented client-side memoized filtering (`filterCytoscapeElements`) in `GraphCanvasContainer` that filters the loaded element dataset in sub-millisecond time and automatically trims orphan edges whose endpoints no longer qualify.

## Consequences
- 60fps responsive UI during threshold sliding and live search filtering.
- Preserves backend server resources by eliminating redundant subgraph query re-execution.
