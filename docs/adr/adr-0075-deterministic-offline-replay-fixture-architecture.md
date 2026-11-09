# ADR-0075: Deterministic Offline Replay Fixture Architecture for Meta and TikTok

## Status
Accepted

## Context
Testing third-party APIs requires 100% offline predictability and zero live cloud dependencies.

## Decision
Deploy MockInstagramClient and MockTikTokClient fixture players with realistic error subcodes and edge cases.

## Consequences
Enables fast, reliable CI and local verification without live API keys.