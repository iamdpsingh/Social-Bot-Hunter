# ADR-0054: Non-Destructive Dry-Run Preview for Data Retention Sweeps

## Context
Accidental bulk deletion of active investigation data represents an unacceptable operational risk.

## Decision
All data retention purge operations require dry-run support, calculating candidate counts and affected records without executing physical SQL DELETE statements.

## Consequences
- Operators can verify the exact blast radius before committing permanent data removal.
