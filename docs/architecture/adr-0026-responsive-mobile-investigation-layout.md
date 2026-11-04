# ADR 0026: Responsive Mobile-Friendly Investigation Layout

## Status
Accepted

## Context
Security analysts and incident commanders frequently review bot infiltration reports and cluster summaries on mobile devices or tablets during active incidents.

## Decision
Design the layout using CSS Grid and Flexbox with responsive breakpoints: collapsable navigation drawer on screens <1024px, stacked metric cards, and horizontal scroll tables.

## Consequences
- Fully operational interface on viewports ranging from 375px mobile to 4K desktop displays.
