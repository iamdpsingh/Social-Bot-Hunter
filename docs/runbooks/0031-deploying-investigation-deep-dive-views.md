# Runbook 0031: Deploying Investigation Deep-Dive Views

## Objective
Verify investigation workspace (`/investigations/[id]`) and account profile (`/investigations/[id]/accounts/[accountId]`) deployment health.

## Verification Steps
1. Run `npm run build` in `apps/dashboard` and verify all dynamic routes compile (`ƒ /investigations/[id]`).
2. Verify Next.js server starts cleanly with `npm run start`.
3. Curl health endpoint: `curl -s http://localhost:8080/api/v1/health | jq .`.
