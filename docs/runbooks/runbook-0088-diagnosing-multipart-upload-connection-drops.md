# RUNBOOK-0088: Diagnosing Multipart Upload Connection Drops

## Purpose
Resolve client network timeouts or HTTP 499/504 errors on large archive uploads.

## Steps
1. Verify reverse proxy client body size limits (`client_max_body_size 200M`).
2. Inspect keepalive and proxy timeout parameters (`proxy_read_timeout 300s`).
3. Recommend uploading compressed archives rather than uncompressed directories.
