# RUNBOOK-0080: Emergency Circuit-Breaking of Compromised Platform API Keys

## Summary
Immediate isolation when credentials leak or are invalidated.

## Emergency Protocol
1. Unset environment variable in process supervisor.
2. Revoke key in developer portal.
3. Adapter automatically returns NotConfiguredAdapter.