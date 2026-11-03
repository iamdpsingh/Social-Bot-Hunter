# ADR-0008: Asynchronous Background Job Engine Architecture

## Status
Accepted

## Context
Full investigation scans evaluate thousands of social accounts, calculate graph similarity metrics, and perform iterative community clustering. Executing these computations synchronously in HTTP request handlers blocks API worker processes and triggers client gateway timeouts.

## Decision
Implement an in-memory priority-based background job engine (`sbh.pipeline.worker`) utilizing bounded Python threading queues and thread worker pools. Scans transition through formal states (`pending` -> `running` -> `complete` / `partial` / `failed`) with atomic optimistic locking.

## Consequences
- HTTP requests return immediately with `201 Created` or `202 Accepted` and the scan identifier.
- Workers execute independently with bounded concurrency, protecting host CPU and memory.
- Worker heartbeats and thread cancellation tokens permit graceful shutdown without orphaned scans.
