# Testing Rules

These rules govern automated testing standards across unit, integration, data-quality, and security suites.

## Principles

1. **Test with Every Feature**: Add automated tests with every material change, new feature, or rule definition.
2. **Regression First**: Reproduce every discovered bug with a failing test before applying the fix, and keep the test as a regression check.
3. **No Weakening Assertions**: Never loosen assertions, increase tolerances without mathematical justification, or delete tests just to achieve a passing test run.
4. **Transparent Skipping**: Do not skip tests silently. Any `@unittest.skip` must carry an explicit reason (e.g., waiting for live credentials or specific database container).
5. **Report Actual Results**: When reporting test execution, state exact test counts, duration, and pass/fail/skip status from terminal output. Never claim tests pass without running them.
6. **Deterministic Fixtures**: Unit tests must execute deterministically without relying on network calls, active internet connections, or unstable external APIs.
