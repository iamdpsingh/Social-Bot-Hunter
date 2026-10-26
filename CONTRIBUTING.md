# Contributing

Read [.agents/rules/](.agents/rules/) first. They apply to people and to coding agents equally.

## Before you push

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -t .   # all tests
python -m sbh docs                                          # generated docs current
ruff check src tests                                        # lint (CI enforces this)
mypy                                                        # types (CI reports; not yet blocking)
```

If `python -m sbh docs` fails, run `python -m sbh docs --write` and commit the result.

## Rules that are easy to break

* A bug fix starts with a failing test that reproduces it.
* Never turn a missing value into `0`. Return an unavailable result with a reason.
* Never describe partial data as complete.
* Schema change: add a new `db/migrations/NNNN_name.sql`. Do not edit an applied one. Add the table to
  `TABLE_DOCS` in `src/sbh/docgen.py` and regenerate the docs.
* Changing a weight, threshold or limit: edit `src/sbh/resources/detection.v1.yaml` **and bump
  `version`**. The database refuses a reused version name with different content.
* Changing what a feature means: bump `FEATURE_VERSION` in `src/sbh/features/definitions.py`.
* Do not log usernames, post text or tokens. Do not store raw post text.
* Do not report a model-quality number that did not come from a real, documented evaluation.

## Adding a platform adapter

1. Research the platform's current official documentation using the checklist in
   [docs/platform-access-matrix.md](docs/platform-access-matrix.md). Record sources and dates.
2. Implement `sbh.contracts.adapter.PlatformAdapter` in its own module. Return the existing record
   types so validation and storage are shared. Use `AccessOutcome` for denial, approval and rate limits,
   and `shared.retry.retry_with_backoff` for transient errors only.
3. Add the capability entries with the real endpoint, API version and scopes. Status is `implemented`
   until a real integration test has passed against an authorised environment, and only then `verified`.
4. Keep credentials out of the repository. Tests use recorded fixtures, clearly labelled.
5. Update the access matrix and `docs/status.md`.

## Adding a feature or rule

Add the feature function and its catalogue entry, then (if it scores) a rule in the YAML. Tests must
cover: the normal case, each unavailable case with its reason, and an edge case at the threshold. Update
`docs/detection-methodology.md`.

## Pull request checklist

- [ ] Tests added or updated, and the whole suite run (say how many passed)
- [ ] Docs updated; `python -m sbh docs` is clean
- [ ] New limitations or unverified parts recorded in `docs/status.md`
- [ ] No credentials, no personal data, no raw post text
