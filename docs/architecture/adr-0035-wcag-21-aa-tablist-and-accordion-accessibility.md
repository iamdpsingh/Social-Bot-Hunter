# ADR 0035: WCAG 2.1 AA Tablist and Accordion Accessibility

## Status
Accepted

## Context
Screen reader users must be able to navigate investigation workspaces and expand evidence without visual reliance.

## Decision
Equip `InvestigationTabs` with `role="tablist"` and `aria-selected` attributes, and `EvidenceInspector` with `aria-expanded` and `aria-controls` targeting regional panels.

## Consequences
- Full screen reader compatibility verified in CI.
- Accessible keyboard tab and arrow key navigation.
