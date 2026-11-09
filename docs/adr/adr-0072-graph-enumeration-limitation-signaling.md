# ADR-0072: Graph Enumeration Limitation Signaling (Follower & Following Restrictions)

## Status
Accepted

## Context
Neither Instagram Business Discovery nor TikTok Research APIs allow enumerating full public follower lists.

## Decision
Return AccessOutcome.REQUIRES_APPROVAL on list_followers and list_following with clear disclosures.

## Consequences
Prevents false negative assumptions in graph analysis.