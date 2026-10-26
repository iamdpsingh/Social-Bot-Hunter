# ADR-0008: Tests written with `unittest`

**Status:** accepted

**Context.** The build environment had no network and no pytest. The CI target uses pytest.

**Decision.** Write tests as `unittest.TestCase` classes. They run with
`python -m unittest discover -s tests -t .` and are collected unchanged by pytest.

**Consequences.** No pytest fixtures or parametrisation (`subTest` is used instead). pytest-only
features can be adopted later without rewriting existing tests.
