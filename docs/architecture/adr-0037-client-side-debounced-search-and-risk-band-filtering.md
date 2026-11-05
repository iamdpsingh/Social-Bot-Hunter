# ADR 0037: Client-Side Debounced Search and Risk Band Filtering

## Status
Accepted

## Context
Typing in the follower explorer search bar should filter rows without triggering excessive API re-fetching on every keystroke.

## Decision
Implement a custom `useDebounce` hook (`250ms` window) coupled with client-side comparator pipelines for multi-attribute sorting and risk band filtering.

## Consequences
- Instant UI responsiveness with minimal network load.
- Seamless search experience across thousands of cached accounts.
