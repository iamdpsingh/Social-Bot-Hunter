# RUNBOOK-0103: Database Failover & Point-in-Time Restore

## Scope & Target
Restoring database state following data corruption or host replacement.

## Operational Procedure
1. Locate most recent verified backup artifact in `data/backups/`: `ls -lt data/backups/*.db.gz`
2. Verify backup checksum: `python -m sbh db-verify <backup_path>`
3. Execute safe restore: `python -m sbh db-restore --input <backup_path> --db ./sbh-dev.sqlite`
4. Confirm database integrity: `python -m sbh doctor`
