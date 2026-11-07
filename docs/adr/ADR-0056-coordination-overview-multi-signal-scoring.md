# ADR-0056: Composite Multi-Signal Coordination Scoring Model

## Context
A single signal (text similarity or burst timing) in isolation has high false positive rates due to organic trends and copypasta.

## Decision
We calculate a composite coordination confidence score combining:
- Text content SimHash clusters (45% weight)
- Temporal burst synchronization lift (35% weight)
- Shared graph follower hubs (20% weight)

## Consequences
- Significantly higher detection precision against authentic viral events.
