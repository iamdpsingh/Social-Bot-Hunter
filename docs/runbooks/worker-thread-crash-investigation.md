# Runbook: Worker Thread Crash Investigation

## Objective
Isolate and debug uncaught exceptions that terminate background worker execution threads.

## Steps
1. Inspect the standard error and log stream for Python tracebacks.
2. Check `ScanTask.error_message` for captured exception strings.
3. Common culprits:
   - Memory allocation failure during dense NetworkX graph algorithms.
   - Network timeouts when contacting external social media APIs.
   - Malformed Unicode strings in usernames or profile bios.
4. Add regression test in `tests/pipeline/` reproducing the failing input payload.
