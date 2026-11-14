# RUNBOOK-0107: High-Volume Scrape Backoff & Jitter Tuning

## Scope & Target
Preventing IP-level bans and handling HTTP 429 rate limits from social platform APIs.

## Operational Procedure
1. Check adapter telemetry in dashboard or logs for `status_code=429`.
2. Inspect `sbh.adapters.rate_limiter` configuration:
   - Base backoff delay: 2.0s
   - Max backoff delay: 60.0s
   - Jitter factor: &plusmn; 25%
3. If persistent 429 errors occur, reduce worker batch concurrency to 1.
