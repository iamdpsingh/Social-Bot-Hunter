# ADR-0084: NDJSON Streaming Ingestion and Quarantine Routing

## Status
Accepted

## Context
Large social data feeds are provided as newline-delimited JSON (NDJSON) where individual corrupt lines must not abort entire ingestion jobs.

## Decision
Stream lines lazily; valid items map to `ContentRecord` or `AccountObservationRecord`, while corrupt or malformed lines are routed to `QuarantinedRecord` with line number provenance.

## Consequences
High fault tolerance and clear diagnostic visibility into bad records.
