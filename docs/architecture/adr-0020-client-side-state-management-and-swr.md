# ADR 0020: Client-Side State Management and SWR Caching

## Status
Accepted

## Context
The dashboard consumes multiple REST endpoints (scans, accounts, capabilities, health, audit logs). We must prevent redundant network requests and provide automatic background revalidation without the boilerplate of Redux or MobX.

## Decision
Adopt Stale-While-Revalidate (SWR) for remote data fetching and caching. Wrap API interactions in typed hooks (`useHealth`, `useScans`, `useCapabilities`, `useAudit`).

## Consequences
- Automatic request deduplication and focus revalidation.
- Optimistic mutations for scan cancellation and retry actions.
- Negligible client bundle footprint (<5KB).
