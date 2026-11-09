# ADR-0076: Telemetry and Latency Tracking Across Third-Party Platform Providers

## Status
Accepted

## Context
Operators need real-time visibility into adapter latency, error spikes, and endpoint call distribution.

## Decision
Record all adapter calls, error rates, and latencies via AdapterTelemetryManager.

## Consequences
Provides real-time operational insights on dashboard and REST endpoints.