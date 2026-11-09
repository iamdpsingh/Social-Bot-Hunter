# ADR-0071: Non-Consented and Private Profile Access Outcomes

## Status
Accepted

## Context
Private accounts on Instagram and TikTok cannot be accessed via public business or research APIs.

## Decision
Explicitly return AccessOutcome.REQUIRES_APPROVAL with a transparent limitation string explaining why private accounts cannot be collected.

## Consequences
Preserves honest limitation disclosure with zero synthetic zeros.