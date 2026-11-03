# ADR-0017: Graceful Worker Shutdown and Queue Draining

## Status
Accepted

## Context
Application server restarts or deployments should not abruptly abort mid-flight scans or leave transactions uncommitted.

## Decision
`WorkerPool.stop(timeout=5.0)` signals a shutdown event, interrupts idle queue waits, allows current active stages to reach the next checkpoint commit, and gracefully joins all worker threads.

## Consequences
- Zero database corruption or half-written records during server shutdowns.
- Clean process termination compatible with Docker and Kubernetes SIGTERM lifecycle.
