# ADR 0032: Client and Server Streaming Export Pipeline

## Status
Accepted

## Context
Downloading complete investigation datasets must support both browser-side immediate table dumping and server-side authorized CSV/JSON streaming.

## Decision
Provide dual export endpoints (`/scans/{id}/export/csv` and `/scans/{id}/export/json`) streaming formatted rows directly with audit log tracking.

## Consequences
- Zero server-side memory buffering for large multi-thousand account exports.
- Instant client-side download feedback with progress feedback.
