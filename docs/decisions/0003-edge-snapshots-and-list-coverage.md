# ADR-0003: Per-scan edge snapshots with explicit list coverage

**Status:** accepted

**Context.** The specification asks that a relationship which disappears from a later observation be
classified as a *confirmed removal* or an *incomplete collection*, and that observed subsets be
distinguished from complete lists.

**Decision.** `relationship_edges` has the grain (scan, source, target, type): each scan stores
what it observed. `relationship_list_coverage` records, per (scan, account, `followers`|`following`),
whether the observed list is `complete`, `partial` or `unknown`. Comparison is computed on demand by
`diff_edge_sets`: an absence is confirmed only when a complete list that would contain the edge
exists in the later scan, and an addition is confirmed only when one existed in the earlier scan.

**Alternatives.** A single mutable "current edges" table with removal flags. Rejected: it has state
that can be corrupted by a partial scan, and loses what each scan actually saw.

**Consequences.** More rows per repeated scan (storage grows with scan count; the retention sweep
exists for this). Comparison logic is a pure function and fully tested. A dataset that never declares
coverage yields `unknown`, so its scans are `partial` and its diffs report nothing as confirmed.
