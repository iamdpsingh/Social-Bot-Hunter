# ADR-0105: Relational Data Dictionary & Schema Standardization

## Status
Accepted

## Context
Dual database support (SQLite and PostgreSQL) requires unambiguous documentation of column data types, constraints, and index strategies.

## Decision
Publish `docs/data-dictionary.md` detailing tables `scans`, `platform_accounts`, `account_observations`, and `coordination_campaigns`, including foreign keys and indexes.

## Consequences
Maintains strict schema parity across SQLite development and PostgreSQL production environments.
