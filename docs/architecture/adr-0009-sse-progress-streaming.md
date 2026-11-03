# ADR-0009: Server-Sent Events (SSE) Progress Streaming

## Status
Accepted

## Context
Investigation workspaces require real-time feedback on pipeline progress, stage completion, and error diagnostics without polling the database repeatedly.

## Decision
Expose an HTTP endpoint `GET /api/v1/scans/{scan_id}/events` streaming Server-Sent Events (`text/event-stream`). The service uses an in-memory pub/sub broker (`ScanEventBroadcaster`) with a circular ring-buffer history supporting `Last-Event-ID` reconnection replay.

## Consequences
- Minimal network overhead compared to frequent REST polling.
- Zero external message broker dependencies (Kafka, Redis) required for local operation.
- Unsubscribing clients disconnect cleanly without resource leaks.
