# Engineering Rules

These rules govern code construction and architectural conventions for Social Bot Hunter.

## Principles

1. **Small, Cohesive Modules**: Keep files focused on a single responsibility. Avoid giant multi-thousand-line modules.
2. **Explicit Types & Interfaces**: Always use type hints and clear interfaces (`Protocol`, Pydantic models, or typed dataclasses). Do not pass untyped dictionaries across module boundaries.
3. **Layer Separation**: Maintain clean separation between:
   - API endpoints & route handlers
   - Domain business logic & feature computation
   - Persistence & SQL repositories
   - Platform integration adapters
4. **No Duplicated Business Logic**: Scoring formulas, threshold evaluations, and normalisation routines must reside in authoritative single-source modules.
5. **Configuration over Hardcoding**: Use YAML configuration and environment variables rather than hardcoding numbers, timeouts, limits, or weights.
6. **Explicit Error Handling**: Handle specific exceptions, log actionable context, and avoid bare `except:` clauses.
7. **Meaningful Comments**: Add comments explaining non-obvious design trade-offs, algorithmic constraints, or edge-case handling. Avoid comments that merely re-state what the code obviously does.
