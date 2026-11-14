# ADR-0104: System Limitations Log & Bounded Scope Specification

## Status
Accepted

## Context
Transparent disclosure of system boundaries and environmental constraints is required for enterprise and forensic software.

## Decision
Maintain `docs/verification/limitations-log.md` detailing public API rate limit boundaries, in-memory Cytoscape node ceilings (5,000 nodes), CPU-only ML throughput, and offline air-gapped behavior.

## Consequences
Sets clear operational expectations for analysts and prevents misinterpreting platform limits as system defects.
