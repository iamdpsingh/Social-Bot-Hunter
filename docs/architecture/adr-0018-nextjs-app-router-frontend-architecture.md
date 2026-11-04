# ADR 0018: Next.js App Router Architecture for Investigation Workspace

## Status
Accepted

## Context
Social Bot Hunter requires an interactive investigation dashboard capable of displaying complex graph structures, live Server-Sent Events, account timelines, and comparative scan diffs. We must select a frontend architecture that supports rapid client-side rendering, strict TypeScript safety, and separation of concerns.

## Decision
Adopt Next.js 14 with the App Router model in `apps/dashboard`. Use React 18 client components for interactive telemetry and visualizations, with centralized layouts, error boundaries, and loading skeletons.

## Consequences
- High developer ergonomics with directory-based routing.
- Fast build times and isolated client state management.
- Zero server-side runtime dependency on Node.js in production (static export or standalone container).
