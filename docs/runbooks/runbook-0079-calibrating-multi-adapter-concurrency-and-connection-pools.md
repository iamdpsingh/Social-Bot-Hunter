# RUNBOOK-0079: Calibrating Multi-Adapter Concurrency and Connection Pools

## Summary
Tuning HTTP client connection pools across YouTube, X, Instagram, and TikTok.

## Settings
- Pool size: 20 per host
- Keepalive timeout: 30s
- Read timeout: 10s