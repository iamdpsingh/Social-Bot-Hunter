# ADR-0100: Cytoscape Graph Serialization & Element Contract

## Status
Accepted

## Context
The Next.js 14 frontend renders network graphs using Cytoscape.js, requiring a strictly compliant JSON schema with zero orphan edges.

## Decision
Implement `sbh.e2e.cytoscape.CytoscapeValidator` verifying that every node has `id` and `label`, every edge references valid existing source and target nodes, and edge IDs follow `source->target` syntax.

## Consequences
Eliminates frontend rendering crashes and dangling edge exceptions on large relationship topologies.
