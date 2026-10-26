# ADR-0006: A capability registry that records what is not known

**Status:** accepted

**Context.** Platforms differ widely in what they expose, terms change, and the specification forbids
inventing endpoints, fields or permissions.

**Decision.** Every (platform, operation) has a registry entry with a status from a fixed
vocabulary. Live operations start as `not_configured` with `supported = unknown` and **no endpoint,
scope or API version**. `Capability` refuses `verified` without a verification date and an evidence
reference, and refuses `implemented` for an official-API operation without an endpoint and version. The
database repeats the `verified` rule as a CHECK constraint. `docs/platform-access-matrix.md` embeds a
table generated from the registry and is checked in CI.

**Consequences.** The table is less impressive than a filled-in one, and accurate. Filling it in is a
research task (checklist in the matrix document), done per platform before any adapter is written.
