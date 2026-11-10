# RUNBOOK-0090: Emergency Purge of Quarantined Malicious Archives

## Purpose
Safely remove suspicious or weaponized archive files from server disk storage.

## Steps
1. Verify file hash against security incident ticket.
2. Securely wipe temp directory using `shred -u` or unlink.
3. Audit log removal action.
