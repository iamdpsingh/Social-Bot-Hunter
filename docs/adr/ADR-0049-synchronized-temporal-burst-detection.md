# ADR-0049: Synchronized Temporal Posting Burst Detection and Poisson Lift Modeling

## Context
Astroturfing campaigns deploy coordinated accounts that post in near-synchronous time windows to manipulate trending algorithms.

## Decision
We implement a temporal co-posting detection algorithm calculating observed co-occurring posts within a configurable window (e.g. 60 seconds) against a uniform random Poisson expectation baseline (lift ratio).

## Consequences
- Abnormal co-posting spikes (>1.5x lift) are flagged as suspicious temporal bursts.
- Documented limitation: natural viral events can elevate lift organically, so timing is evaluated alongside content and graph signals.
