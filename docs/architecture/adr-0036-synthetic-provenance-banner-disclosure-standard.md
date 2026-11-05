# ADR 0036: Synthetic Provenance Banner Disclosure Standard

## Status
Accepted

## Context
To prevent ethical harm, datasets generated for testing must never be mistaken for empirical accusations against live social media accounts.

## Decision
Prominently display `SyntheticDataBanner` across `/investigations` archives, investigation workspaces, and account deep dive pages whenever data origin is synthetic.

## Consequences
- Unambiguous visual warning banner on all demo data views.
- Provenance flags exported in all CSV and JSON headers.
