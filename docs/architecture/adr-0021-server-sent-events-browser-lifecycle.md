# ADR 0021: Server-Sent Events (SSE) Browser Lifecycle Management

## Status
Accepted

## Context
Live collection jobs stream progress events over HTTP (`/scans/{id}/events`). Browsers must handle connection drops, page unmounts, and terminal status events without leaking sockets.

## Decision
Implement `useScanEvents` hook using browser-native `EventSource`. Pass auth token via query parameter or header shim, auto-close stream on terminal states (`completed`, `failed`, `cancelled`), and cleanly close in effect cleanup.

## Consequences
- Reliable real-time progress updates with 0ms polling delay.
- Guaranteed socket cleanup on route change.
