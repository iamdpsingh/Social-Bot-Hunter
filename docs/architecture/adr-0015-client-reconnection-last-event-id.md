# ADR-0015: SSE Client Reconnection and Event Replay

## Status
Accepted

## Context
Browser tabs and mobile dashboards frequently suffer temporary network disconnections during multi-minute scan investigations.

## Decision
Each `ScanEvent` carries a monotonically generated identifier (`evt_<hex>`). `ScanEventBroadcaster` maintains a circular buffer of recent events. When an SSE client reconnects with `Last-Event-ID`, missed events are replayed before switching to live stream.

## Consequences
- Smooth, uninterrupted UI progress bars across network glitches.
- Zero missing stage completion alerts or terminal error notifications.
