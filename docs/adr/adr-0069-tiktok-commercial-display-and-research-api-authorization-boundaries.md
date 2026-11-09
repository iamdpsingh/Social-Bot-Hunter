# ADR-0069: TikTok Commercial Display and Research API Authorization Boundaries

## Status
Accepted

## Context
TikTok integrations require rigorous differentiation between Research API v2 credentials and Display API.

## Decision
Implement TikTokAdapter conforming to TikTok Research API v2 contracts, isolating private accounts and minor accounts under AccessOutcome.REQUIRES_APPROVAL.

## Consequences
Ensures complete compliance with TikTok Terms of Service and data protection laws.