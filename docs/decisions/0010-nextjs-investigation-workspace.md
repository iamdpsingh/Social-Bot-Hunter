# ADR-0010: Next.js and Cytoscape.js for Investigation Dashboard

**Status:** accepted

**Context.** The platform requires an interactive, accessible investigation workspace with 7 core views: Overview, Account Investigation, Follower/Following Explorer, Network Explorer, Coordinated Activity, Scan History, and Data Sources/Settings.

**Decision.** Build the frontend in `apps/dashboard` using Next.js (App Router), TypeScript, and a unified design system.
1. Use Cytoscape.js for directed network graph rendering with layout algorithms (cose-bilkent / dagre) and interactive node/edge inspection panels.
2. Provide accessible tabular fallback views for every graph and network cluster to ensure accessibility and support large graphs.
3. Distinguish risk categories with both color and distinct visual icons/shapes/badges so color is never the sole indicator.
4. Distinguish observed subsets from full platform lists prominently in all UI views.
5. Provide a clear visual banner when viewing synthetic demo datasets or test fixtures.

**Alternatives.**
- Sigma.js / WebGL: Sigma is high performance for >50k nodes but less flexible for fine-grained node inspection and small directed subgraphs. Cytoscape.js offers rich styling, event handling, and layout options.
- Client-only SPA (Vite): Lacks server-side rendering, secure proxying for API tokens, and streaming responses.

**Consequences.** Delivers a professional, evidence-first analyst interface connected to the `/api/v1` backend rather than disconnected mock screens.
