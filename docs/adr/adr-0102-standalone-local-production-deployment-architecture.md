# ADR-0102: Standalone Local Production Deployment Architecture

## Status
Accepted

## Context
Users require a privacy-preserving investigation tool that runs entirely on local machines without transmitting data to cloud platforms.

## Decision
Standardize on a local `.venv` deployment using `scripts/run_local.sh`, coordinating FastAPI, local SQLite/PostgreSQL, a multiprocessing worker, and the Next.js frontend with zero cloud SDKs or SaaS telemetry.

## Consequences
Guarantees 100% data sovereign operational capabilities for sensitive forensic workflows.
