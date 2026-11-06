# ADR-0039: Multi-Layout Engine Presets Architecture

## Status
Accepted

## Context
Different threat investigation scenarios require different topological layouts: bot swarms cluster best in force-directed physics, while hierarchical astroturfing campaigns require concentric or breadthfirst tree projections.

## Decision
Implemented 5 layout presets via `getLayoutOptions`:
1. `cose`: Physics-based force-directed clustering.
2. `concentric`: Radial rings ordered by risk score (critical in center, low on perimeter).
3. `circle`: Circular perimeter layout for ring detection.
4. `breadthfirst`: Directed hierarchy from root influencers.
5. `grid`: Compact tabular alignment.

## Consequences
- Analysts can switch layouts with a single toolbar dropdown without re-fetching graph data.
- Layout transitions are animated smoothly (300-500ms) with zero jank.
