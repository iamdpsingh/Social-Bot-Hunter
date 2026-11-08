# ADR-0066: Adapter Latency and Error Telemetry Aggregation

## Context
Social Bot Hunter requires reliable, compliant third-party social data ingestion while strictly preventing
SSRF vulnerabilities, third-party API ban cascades, and billing surprises.

## Decision
Track real-time request counts, error spikes, and endpoint durations in AdapterTelemetryManager.

## Consequences
- Guarantees predictable operational expenditures.
- Fully preserves test determinism without live cloud dependencies.
- Enforces strict security boundaries on external URL inputs.
