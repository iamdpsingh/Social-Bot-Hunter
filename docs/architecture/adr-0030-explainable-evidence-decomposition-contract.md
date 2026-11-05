# ADR 0030: Explainable Evidence Decomposition Contract

## Status
Accepted

## Context
Black-box risk scores fail regulatory compliance and security audits. Analysts need exact rule names, relative weights, and observed evidence summaries.

## Decision
Enforce a formal evidence decomposition schema (`contributions`: array of rule name, weight, value, and description) in all account assessments.

## Consequences
- Complete transparency into bot probability calculations.
- Verifiable proof for audit compliance and defensible moderation.
