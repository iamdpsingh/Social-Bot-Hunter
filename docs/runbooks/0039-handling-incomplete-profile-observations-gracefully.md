# Runbook 0039: Handling Incomplete Profile Observations Gracefully

## Objective
Remediate accounts with deleted profiles, private privacy settings, or missing avatars.

## Triage Actions
1. Verify `AccountProfileCard` uses initials fallback when username is null.
2. Confirm `LimitationsCard` discloses private account API limitations.
3. Check `RiskGauge` falls back to `N/A` when scores are undefined.
