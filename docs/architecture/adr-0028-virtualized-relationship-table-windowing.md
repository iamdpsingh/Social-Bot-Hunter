# ADR 0028: Virtualized Relationship Table Windowing

## Status
Accepted

## Context
Investigations often uncover bot networks spanning 10,000+ follower and following edges. Rendering raw DOM rows crashes mobile browsers and degrades 60fps frame rate.

## Decision
Adopt windowed table virtualization with fixed row heights (`52px`), viewport overscan (`5` rows above and below), and dynamic scroll slicing.

## Consequences
- Constant DOM node footprint (< 25 nodes) regardless of relationship volume.
- Fluid 60fps scrolling performance on low-power devices.
