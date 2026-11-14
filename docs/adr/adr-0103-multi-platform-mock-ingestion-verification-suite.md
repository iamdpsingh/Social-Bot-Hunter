# ADR-0103: Multi-Platform Mock Ingestion Verification Suite

## Status
Accepted

## Context
Testing multi-platform bot detection cannot rely on flaky, rate-limited public APIs during automated CI runs.

## Decision
Implement `MultiPlatformMockGenerator` in `sbh.e2e.platforms` creating realistic, synthetic bot campaigns and human accounts for Twitter/X, Bluesky, Mastodon, Reddit, and YouTube.

## Consequences
Enables deterministic, fast, offline regression tests across all 5 supported social networks.
