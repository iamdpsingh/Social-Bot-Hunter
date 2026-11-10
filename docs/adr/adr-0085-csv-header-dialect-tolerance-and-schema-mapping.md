# ADR-0085: CSV Header Dialect Tolerance and Schema Mapping

## Status
Accepted

## Context
CSV data dumps from external tools vary in header casing, whitespace, and column names (`user_id` vs `author_id` vs `author`).

## Decision
Normalize CSV headers by trimming whitespace and lowercasing, matching against prioritized synonym dictionaries.

## Consequences
Supports exports from popular research tools (Gephi, NodeXL, academic scrapers) out-of-the-box.
