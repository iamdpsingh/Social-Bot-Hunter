# ADR-0047: Dual-Surface Integration: Workspace Tab and Fullscreen Explorer Route

## Status
Accepted

## Context
Analysts need both quick network previews inside the main investigation overview workspace and an immersive full-screen canvas for deep graph exploration.

## Decision
Provided dual surfaces:
1. Workspace Tab: Added "Interactive Network Explorer" tab in `InvestigationTabs` on `/investigations/[id]`.
2. Dedicated Route: `/investigations/[id]/graph` providing dedicated breadcrumbs, metrics cards, toolbar, filter panel, and drawer.

## Consequences
- Intuitive navigation matching user mental model.
- Deep linkable URLs for specific graph investigations.
