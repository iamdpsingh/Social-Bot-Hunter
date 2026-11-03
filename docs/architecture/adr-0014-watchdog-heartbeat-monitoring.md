# ADR-0014: Worker Thread Watchdog Heartbeat Monitoring

## Status
Accepted

## Context
Worker threads executing third-party API adapters or complex graph computations may freeze or enter deadlock states silently.

## Decision
Implement a heartbeat registry in `WorkerPool` where each worker records its UNIX timestamp upon loop iteration and stage transition. An external health check flags workers silent for more than 120 seconds.

## Consequences
- Rapid detection and alerting of deadlocked or unresponsive worker threads.
- Enables automated scan timeout transitions and operator notifications.
