# RUNBOOK-0077: Diagnosing SSRF Validation False Positives in Live Probes

## Summary
Investigate valid external profile URLs erroneously flagged by SSRF guardrails.

## Troubleshooting
1. Check IP address resolution of target hostname.
2. Ensure CDN egress IPs are not in RFC1918 space.