# ADR 0023: Synthetic Provenance Disclosure Patterns

## Status
Accepted

## Context
The platform supports testing with synthetic fixtures. Showing synthetic demonstration data without clear warnings could cause analysts or executives to mistake simulated bot clusters for real user accounts.

## Decision
Display persistent, high-visibility `SyntheticDataBanner` disclaimers whenever synthetic datasets are imported or viewed. Display `PROVENANCE: SYNTHETIC` tags in tables and account profile cards.

## Consequences
- Prevents false accusations against real platform users.
- Enforces strict ethical boundaries outlined in the project vision.
