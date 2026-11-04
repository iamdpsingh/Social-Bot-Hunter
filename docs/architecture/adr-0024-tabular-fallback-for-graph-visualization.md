# ADR 0024: Accessible Tabular Fallbacks for Graph Visualizations

## Status
Accepted

## Context
Force-directed graph canvases (Cytoscape.js) are visually intuitive but inaccessible to assistive technologies and unreadable when node counts exceed 5,000.

## Decision
Every graph-centric view must provide a synchronized tabular representation. The table supports full sorting, pagination, search debounce, and CSV export.

## Consequences
- Full accessibility for keyboard-only and screen reader users.
- Scalable inspection fallback for large-scale social networks.
