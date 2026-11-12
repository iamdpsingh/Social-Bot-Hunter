# Storage Retention Engine and Least-Recently-Used Eviction Policy

- **Status**: Accepted
- **Date**: 2026-11-12
- **Milestone**: Day 12 (Local Venv Runtime Orchestration, Process Management & Storage Hardening)

## Context
Social Bot Hunter is designed as an enterprise-grade, privacy-first bot detection platform capable of running fully locally within an isolated virtual environment (`.venv`) without mandatory cloud queues, serverless engines, or third-party storage buckets.

## Decision
Enforces deterministic LRU and TTL cleanup while guaranteeing minimum count and protecting production ML models.

## Implementation Details
1. Architected strictly within the repository without requiring root permissions or external background services.
2. Protected against path traversal vulnerabilities, stale lock corruption, and silent data loss.
3. Fully integrated with automated testing, linting, and type verification.

## Consequences
- **Positive**: Complete offline autonomy, zero cloud bill, instant setup for local analysts and air-gapped forensic investigations.
- **Trade-offs**: Local concurrency bounded by host machine CPU cores and available disk capacity.
