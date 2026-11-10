# RUNBOOK-0084: Recovering from Archive Temp Storage Disk Exhaustion

## Purpose
Clear stale uncompressed archive artifacts if temporary scratch directories exceed quota.

## Steps
1. Check `/tmp/sbh_archive_*` directories.
2. Run automated scratch cleanup script `scripts/cleanup_stale_archives.py`.
3. Verify ephemeral volume quota.
