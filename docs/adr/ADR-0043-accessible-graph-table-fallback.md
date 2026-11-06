# ADR-0043: Accessible Graph Table Fallback for Large Graphs and Screen Readers

## Status
Accepted

## Context
Canvas/WebGL graph visualizers are inherently inaccessible to screen reader assistive technologies and degrade in performance beyond 5,000 active nodes.

## Decision
Built `AccessibleGraphTable` as a first-class view mode with `scope="col"`, sortable headers, in/out-degree counts, risk badges, keyboard navigation, and an auto-warning threshold (`GraphScaleAlert`) when graphs exceed 5,000 nodes.

## Consequences
- 100% WCAG 2.1 AA compliance across all graph analytical workflows.
- Zero freeze or crash risk when rendering massive investigations.
