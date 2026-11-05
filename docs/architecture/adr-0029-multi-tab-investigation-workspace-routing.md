# ADR 0029: Multi-Tab Investigation Workspace Routing

## Status
Accepted

## Context
Analysts require simultaneous access to high-level scan metadata, granular relationship tables, feature matrices, and export tools without page reloads.

## Decision
Implement a multi-tab workspace layout (`/investigations/[id]`) with client-side view switching and accessible ARIA tablist navigation.

## Consequences
- Zero layout thrashing between overview, explorer, features, and export views.
- Deep-linkable state preserved across investigation sessions.
