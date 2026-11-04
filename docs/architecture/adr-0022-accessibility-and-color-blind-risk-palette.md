# ADR 0022: Accessibility and Color-Blind Safe Risk Palette

## Status
Accepted

## Context
Automated bot detection platforms frequently use red/amber/green indicators. For analysts with color vision deficiencies, reliance on color alone violates WCAG 2.1 AA and leads to critical misinterpretation.

## Decision
Mandate the Dual-Indicator Rule across all risk representations: every score or band badge must combine color with distinct iconography (`ShieldAlert`, `AlertTriangle`, `AlertCircle`, `ShieldCheck`), textual labels, and numeric percentages.

## Consequences
- 100% WCAG 2.1 AA compliant risk presentation.
- Accessible to screen readers via explicit ARIA labels.
