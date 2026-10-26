# ADR-0001: One Python package instead of several

**Status:** accepted

**Context.** The specification sketches `packages/platform_contracts`, `packages/schemas`,
`packages/graph_analysis`, `packages/shared` and several `workers/*` directories.

**Decision.** One installable package, `sbh`, with sub-packages for the same responsibilities
(`contracts`, `schemas`, `graph`, `shared`, `features`, `detection`, `storage`, `pipeline`). Workers
will be thin entry points over it when the queue-based deployment exists.

**Alternatives.** Many distributions with their own `pyproject.toml`. Rejected for now: it adds
version-pinning and import-path friction without any deployable unit that needs it.

**Consequences.** Simple to test and refactor. Module boundaries are enforced by convention (features,
detection and graph are pure and do not import storage writes), not by packaging. Split a package out
when a deployable unit, a different release cadence or a different dependency set requires it.
