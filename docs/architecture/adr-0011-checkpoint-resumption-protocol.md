# ADR-0011: Checkpoint Resumption Protocol

## Status
Accepted

## Context
Hardware reboots, system crashes, or out-of-memory events can interrupt long-running investigations. Re-running entire scans from scratch wastes compute and platform API quotas.

## Decision
Record atomic stage completion checkpoints into `scan_checkpoints` containing stage identifiers, processed row counts, and cursors. On scan retry or worker recovery, scans inspect the latest checkpoint and resume from that stage.

## Consequences
- Scans are crash-resilient and restartable.
- Pipeline stages are idempotent, guaranteeing consistent derived metrics.
