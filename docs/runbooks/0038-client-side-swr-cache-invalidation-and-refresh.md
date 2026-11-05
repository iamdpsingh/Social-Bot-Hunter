# Runbook 0038: Client-Side SWR Cache Invalidation and Refresh

## Objective
Force refresh stale investigation data in the analyst dashboard without full page reloads.

## Execution Steps
1. Call `mutate()` from `useInvestigation(scanId)` or `useRelationships(scanId)`.
2. Verify network panel shows conditional `ETag` / `If-None-Match` requests.
