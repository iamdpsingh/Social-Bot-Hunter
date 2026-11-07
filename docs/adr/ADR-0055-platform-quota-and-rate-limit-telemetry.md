# ADR-0055: Multi-Platform API Quota and Rate Limit Telemetry Standardization

## Context
Different social media platforms impose disparate rate limits (e.g. YouTube quota units vs Twitter RPM).

## Decision
We define a unified `PlatformQuotaStatus` schema standardizing daily quota limit, quota consumed, remaining pool, and request-per-minute thresholds across YouTube, X, TikTok, Instagram, and LinkedIn.

## Consequences
- Provides unified dashboard visibility into platform quota exhaustion risks.
