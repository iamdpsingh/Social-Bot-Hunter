# ADR-0086: Audit Trail Provenance for Archive Upload Events

## Status
Accepted

## Context
Forensic and compliance requirements require full tracking of who uploaded external datasets and when.

## Decision
Every call to `POST /api/v1/imports/archive` records an immutable audit event in `AuditRepository` with actor ID, filename, format, and record counts.

## Consequences
Auditors can reconstruct the provenance of all offline ingested investigation evidence.
