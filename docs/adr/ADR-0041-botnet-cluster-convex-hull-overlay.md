# ADR-0041: Botnet Cluster Convex Hull Visualization Overlay

## Status
Accepted

## Context
When coordinated botnet clusters are detected by community detection algorithms (e.g. weakly connected components), analysts must instantly perceive cluster boundaries without reading tabular IDs.

## Decision
Implemented Monotone Chain convex hull polygon calculation (`computeConvexHull`) rendered via a pointer-events-none SVG overlay (`ClusterHullOverlay`) layered above Cytoscape coordinates with distinct cluster color tints.

## Consequences
- Immediate visual grouping of coordinated bot clusters.
- Low GPU overhead compared to continuous force field rendering.
