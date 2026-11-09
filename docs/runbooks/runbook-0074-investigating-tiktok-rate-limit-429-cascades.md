# RUNBOOK-0074: Investigating TikTok Rate Limit (429) Cascades

## Summary
Resolving TikTok Research API 120 req/min rate limit saturation.

## Mitigation Steps
1. Inspect active scanner concurrency in Worker queue.
2. Trigger automatic backoff sleep of 60 seconds.
3. Review telemetry table on /adapters dashboard.