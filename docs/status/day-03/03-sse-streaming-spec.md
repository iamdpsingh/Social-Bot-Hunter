# Day 3: Server-Sent Events (SSE) Streaming Specification

Endpoint: `GET /api/v1/scans/{scan_id}/events`
- Transport: HTTP/1.1 `text/event-stream`
- Reconnection: `Last-Event-ID` header replay via in-memory ring-buffer.
- Keep-alives: `: ping\n\n` heartbeat frames.
