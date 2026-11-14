# RUNBOOK-0105: Cytoscape Graph Virtualization & Memory Headroom

## Scope & Target
Managing memory usage and canvas responsiveness for large relationship graphs (&gt; 5,000 nodes).

## Operational Procedure
1. Inspect node count returned by `/api/v1/scans/{id}/networks/graph`.
2. For graphs &gt; 5,000 nodes:
   - Enable ego-expansion mode (`depth=1` around suspicious seeds)
   - Filter low-degree singleton nodes (`min_degree=2`)
   - Collapse dense cliques into cluster convex hulls
3. Verify browser tab heap remains &lt; 300MB.
