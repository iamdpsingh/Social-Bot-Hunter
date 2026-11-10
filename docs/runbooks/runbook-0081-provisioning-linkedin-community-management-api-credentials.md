# RUNBOOK-0081: Provisioning LinkedIn Community Management API Credentials

## Purpose
Configure LinkedIn OAuth 2.0 application credentials for organization timeline inspection.

## Steps
1. Register App in LinkedIn Developer Portal.
2. Request `r_organization_social` and `rw_organization_admin` scopes.
3. Configure `SBH_LINKEDIN_CLIENT_ID` and `SBH_LINKEDIN_CLIENT_SECRET` in environment.
4. Verify credentials using `.venv/bin/python -m sbh probe https://linkedin.com/company/target`.
