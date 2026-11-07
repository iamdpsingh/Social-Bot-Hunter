# RUNBOOK-0058: Platform API Quota Exhaustion Response

## Purpose
Manage platform rate-limiting and quota exhaustion during large investigations.

## Procedure
1. Check `/settings` to inspect remaining quota pools.
2. If remaining quota < 5%, throttle crawl depth from 3 to 1.
3. Temporarily pause scheduled imports until UTC midnight quota reset.
