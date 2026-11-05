# ADR 0034: Dual-Indicator SVG Risk Gauge Geometry

## Status
Accepted

## Context
Color-alone gauges violate accessibility standards for color-blind users and lack immediate readability on high-DPI displays.

## Decision
Implement `RiskGauge` with SVG circular progress arcs, numeric percentage center readouts, and textual risk band badges (`Critical`, `High`, `Medium`, `Low`).

## Consequences
- WCAG 2.1 AA non-color reliance compliance.
- Vector rendering with zero pixelation across zoom levels.
