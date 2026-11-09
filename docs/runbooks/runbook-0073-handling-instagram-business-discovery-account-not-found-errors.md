# RUNBOOK-0073: Handling Instagram Business Discovery Account Not Found Errors

## Summary
Diagnose whether an error is a true 404 or a personal account subcode (2207050).

## Triage Steps
1. Inspect raw Graph API error payload.
2. If subcode == 2207050, account is personal/private.
3. If subcode == 2207001, account does not exist.
4. Display appropriate badge in UI.