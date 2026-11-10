# ADR-0078: LinkedIn Community Management API Integration Architecture

## Status
Accepted

## Context
LinkedIn enforces stringent anti-scraping and member privacy policies. Graph enumeration (1st-degree connections, followers) is restricted.

## Decision
We integrate LinkedIn via the Community Management API v2 protocol for Organizations and vanity member lookups, enforcing `AccessOutcome.REQUIRES_APPROVAL` on following/connection graphs.

## Consequences
Guarantees compliance with LinkedIn Developer Terms while providing deterministic mock replay for testing organization post timelines.
