# ADR-0101: Offline Subsystem Health Diagnostic Probes

## Status
Accepted

## Context
Operators need an immediate, self-contained health check to diagnose local SQLite, filesystem storage, and model artifacts before launching workers.

## Decision
Implement `sbh.health` with `HealthProbeRunner` and CLI command `sbh doctor`. Probes verify SQLite integrity (`PRAGMA integrity_check`), directory writability, free disk space (&ge; 500MB), and trained model presence.

## Consequences
Operators can diagnose misconfigurations in &lt; 50ms without reading through verbose application logs.
