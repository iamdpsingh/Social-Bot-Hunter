# Social Bot Hunter - X API v2 Integration Specification

## 1. Overview
The X adapter interfaces with X API v2 (formerly Twitter API) to retrieve user profiles,
follower graphs, following graphs, and recent tweets for bot and coordination detection.

## 2. Rate Limit Windows
- **App Rate Limits**: 15-minute sliding windows per endpoint.
  - `/2/users/by/username/:username`: 900 requests / 15 min.
  - `/2/users/:id/followers`: 15 requests / 15 min (Free/Basic tier limit).
  - `/2/users/:id/following`: 15 requests / 15 min.
  - `/2/users/:id/tweets`: 900 requests / 15 min.
- **Handling 429**: When `x-rate-limit-remaining` hits zero, the adapter raises `RateLimitExceededError` with the calculated sleep seconds until `x-rate-limit-reset`.

## 3. SimHash Coordination Ingestion
Every ingested tweet has its 64-bit SimHash near-duplicate fingerprint computed inline
at ingest time using the engine defined in `sbh.detection.simhash`. This allows downstream
scans to detect cross-account synchronized paste campaigns without an extra computation step.
