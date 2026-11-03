# Runbook: Server-Sent Events Connection Limits

## Objective
Prevent file descriptor exhaustion and high memory footprint from idle or abandoned SSE client connections.

## Connection Guidelines
- Maximum concurrent SSE connections per client IP: 10.
- Each connection automatically closes upon scan terminal status (`complete`, `partial`, `failed`, `cancelled`).
- Keep-alive comments (`: ping\n\n`) are sent every 15 seconds to detect dropped network sockets.

## Monitoring
Check active SSE subscriber counts via `ScanEventBroadcaster` metrics or API health checks.
