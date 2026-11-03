# Runbook: Corrupted Checkpoint Recovery

## Objective
Recover from incomplete or malformed checkpoint entries caused by abrupt storage write interruptions.

## Recovery Procedure
1. Check existing checkpoints for the scan:
   ```sql
   SELECT * FROM scan_checkpoints WHERE scan_id = :id ORDER BY committed_at DESC;
   ```
2. If the latest checkpoint has invalid JSON details, delete the corrupted row:
   ```sql
   DELETE FROM scan_checkpoints WHERE scan_id = :id AND stage = :corrupt_stage;
   ```
3. Trigger scan retry; the pipeline runner will safely restart from the previous valid stage checkpoint.
