# ADR 0025: Frontend Testing Strategy with Vitest and JSDOM

## Status
Accepted

## Context
We need fast, reliable unit and component testing for the frontend workspace that runs identically in local environments and GitHub Actions CI without heavy browser daemon overhead.

## Decision
Adopt Vitest with `@testing-library/react` and `jsdom`. Isolate tests by mocking network fetch calls and verifying ARIA roles, event dispatchers, and state transitions.

## Consequences
- Sub-second test execution across all component suites.
- Seamless integration with existing CI pipeline.
