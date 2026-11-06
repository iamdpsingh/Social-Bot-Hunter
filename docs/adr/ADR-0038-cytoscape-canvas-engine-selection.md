# ADR-0038: Selection of Cytoscape.js for Directed Network Visualization

## Status
Accepted

## Context
Analysts need an interactive directed network graph canvas capable of smoothly rendering thousands of nodes and directed edges with custom layouts, directional arrowheads, cluster hulls, and instant node inspection.

## Decision
We adopted `Cytoscape.js` (v3.34.4) for canvas graph rendering in the Next.js frontend, complemented by an Accessible Table alternative for screen readers and scale fallbacks.

## Consequences
- High-performance canvas rendering with native support for force-directed (Cose), concentric, and hierarchical layouts.
- Pure client-side interactions (drag, zoom, pan, select) without continuous backend round-trips.
- Clean separation between visualization and tabular screen-reader modes.
