# Runbook: High-Load Rate Limiting and Backoff Management

## Objective
Manage API client ingestion and platform API rate limits under heavy investigation load.

## Rate Limiting Architecture
- API endpoints are protected by `SimpleRateLimiterMiddleware` (120 req/min default).
- Outbound platform requests use Token Bucket rate limiters per platform account.
- When platform APIs return HTTP 429, the pipeline worker pauses with exponential backoff:
  `sleep = base_sec * (2 ** retry_count)`.
