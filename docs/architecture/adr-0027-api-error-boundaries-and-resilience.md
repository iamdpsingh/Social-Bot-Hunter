# ADR 0027: Frontend API Error Boundaries and Graceful Degradation

## Status
Accepted

## Context
When backend services or platform APIs experience rate limiting (HTTP 429), authentication expiry (HTTP 401), or server errors (HTTP 500), the UI must not white-screen or crash.

## Decision
Implement React Error Boundaries (`app/error.tsx`), typed `ApiError` class with HTTP status parsing, and actionable user retry triggers.

## Consequences
- Graceful degradation with clear user feedback on network anomalies.
- Error isolation preventing entire dashboard crashes.
