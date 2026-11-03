# Runbook: Stuck Scan Remediation

## Objective
Safely release or recover an investigation scan stuck in `running` status following a host crash or unhandled worker termination.

## Criteria
A scan is deemed stuck if:
- `status == 'running'`
- No events have been emitted in >300 seconds.
- The latest checkpoint has not updated.

## Procedure
1. Confirm the scan ID: `sbh list-scans --status running`.
2. Verify no active OS thread is processing the scan.
3. Transition scan to `failed` using `ScanStateMachine` or CLI:
   ```bash
   sbh fail-scan <scan-id> --reason "Worker thread terminated abruptly"
   ```
4. To restart computation from the last valid checkpoint, execute:
   ```bash
   sbh retry-scan <scan-id>
   ```
