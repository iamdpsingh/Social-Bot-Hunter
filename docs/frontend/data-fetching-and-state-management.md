# Data Fetching and State Management

## Architecture
- **SWR Client**: Stale-While-Revalidate caching pattern for queries (`useHealth`, `useScans`, `useCapabilities`, `useAudit`).
- **SSE Stream**: Native browser `EventSource` connection to `/api/v1/scans/{id}/events` for live investigation progress without polling loops.
- **Bearer Authentication**: Automatic JWT injection via `apiClient` with 401 error redirection.
