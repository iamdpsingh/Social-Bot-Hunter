# ADR-0040: Directed Edge Bezier Curves and Arrowhead Styling

## Status
Accepted

## Context
Social bot networks exploit directed relationships: followers, following, retweeting, and mentioning. Visualizing bidirectional and multigraph edges without visual ambiguity requires distinct arrowheads and bezier curve offsets.

## Decision
Styled edges using `curve-style: 'bezier'` with `target-arrow-shape: 'triangle'` pointing from follower to following account. Highlighted edges adopt high-contrast blue (`#3b82f6`) and elevated z-index, while unselected edges dim to 10% opacity.

## Consequences
- Unambiguous visual directionality across follower-following edges.
- High visual contrast preserving WCAG 2.1 AA readability.
