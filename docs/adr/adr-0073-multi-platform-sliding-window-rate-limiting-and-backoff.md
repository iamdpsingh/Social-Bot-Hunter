# ADR-0073: Multi-Platform Sliding Window Rate Limiting and Backoff

## Status
Accepted

## Context
Each platform enforces distinct rate-limit windows (Instagram: 200/hr, TikTok: 120/min, X: 900/15min).

## Decision
Manage per-platform sliding window rate limiters in memory with automatic exponential backoff on HTTP 429.

## Consequences
Prevents API quota bans and maintains system stability.