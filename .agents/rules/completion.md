# Completion Rules

These rules define the required verification workflow before marking any task, phase, or feature complete.

## Verification Checklist

Before marking any task complete:

1. **Verify Acceptance Criteria**: Ensure all acceptance criteria defined in the specification or phase plan are verifiably met.
2. **Execute Relevant Tests**: Run the full relevant test suite (e.g. `PYTHONPATH=src python3 -m unittest discover -s tests -t .`) and verify that all tests pass without unexpected failures or unrecorded skips.
3. **Inspect Output & Behaviour**: Check actual CLI, API, or worker output against expectations (e.g. `python -m sbh demo`).
4. **Update Documentation**: Keep `status.md`, architecture diagrams, data dictionaries, and ADRs up to date.
5. **Record Limitations**: Honestly log known gaps, pending credentials, or uncalibrated heuristics.
6. **Provide Evidence**: In summary handoffs, report exact commands executed, pass counts, run durations, and file paths. Never claim completion without terminal verification.
