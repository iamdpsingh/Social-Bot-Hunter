# RUNBOOK-0071: Provisioning Meta App Review & Instagram Graph API Tokens

## Summary
Step-by-step procedures to configure Meta Developer App permissions (instagram_basic, pages_show_list).

## Prerequisites
- Meta Developer Account
- Connected Instagram Professional Account

## Procedure
1. Generate Long-Lived System User Access Token.
2. Verify token scopes in Meta Access Token Debugger.
3. Configure `INSTAGRAM_GRAPH_TOKEN` environment variable.
4. Execute probe validation test.