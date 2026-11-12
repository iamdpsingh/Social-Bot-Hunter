# Local Background Worker Tuning and Dead-Letter Queue Handling

## Purpose
Diagnosing worker queue backlog, tuning concurrency limits, and inspecting or requeueing dead-letter jobs.

## Target Audience
Local investigators, system administrators, and developers operating Social Bot Hunter in local development or standalone server environments.

## Step-by-Step Instructions
1. **Diagnosis**: Inspect system state and logs using standard CLI tooling (`sbh runtime-status` or `scripts/run_local.sh --status`).
2. **Mitigation**: Follow prescribed resolution steps to restore normal system operations.
3. **Verification**: Confirm healthy operation via automated test suites and health check endpoints.

## Related Documentation
- Master Plan: `docs/14-day-master-plan.md`
- Architecture Decision Records: `docs/adr/`
