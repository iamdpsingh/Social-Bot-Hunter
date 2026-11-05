# Runbook 0035: Resolving WCAG 2.1 AA Compliance Regressions

## Objective
Audit and fix accessibility violations in interactive investigation widgets.

## Audit Actions
1. Run axe / vitest a11y suite: `npm run test -- src/test/a11y/`.
2. Inspect color contrast ratios on risk badges (minimum 4.5:1 text-to-background).
3. Verify all SVG meters include `role="meter"` and `aria-valuenow`.
