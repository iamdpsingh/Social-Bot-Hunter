# Social Bot Hunter - System Limitations Log

This document enumerates the operational boundaries, rate limits, and environmental constraints of Social Bot Hunter v1.0.0.

## 1. Rate Limit & Anti-Scraping Boundaries
- **Twitter/X**: Subject to strict public guest rate limits (typically ~150 requests / 15 minutes). The platform implements automatic exponential backoff with jitter (`sbh.adapters.rate_limiter`). When rate limits are reached, the system gracefully falls back to cached snapshot observations or synthetic demo data.
- **Bluesky**: AT Protocol limits authenticated API requests to 3,000 req / 5 min. Public endpoints are subject to IP-level throttling.
- **Mastodon / Fediverse**: Rate limits vary by decentralized instance (typically 300 requests / 5 minutes). Cross-instance federation hops may experience network latency.
- **Reddit**: Reddit Data API requires OAuth application registration and enforces 100 queries / minute limits.
- **YouTube**: YouTube Data API v3 enforces quota units (10,000 units/day default limit). Comment thread ingestion consumes 1 unit per page.

## 2. In-Memory Graph Scalability Constraints
- **Graph Canvas Node Ceiling**: The Cytoscape.js canvas in `apps/dashboard` renders smoothly up to 5,000 nodes and 20,000 edges using WebGL/Canvas 2D.
- **Virtualization Recommendation**: Networks with > 5,000 nodes are automatically filtered to show top ego neighborhoods, high-degree hub nodes, and coordinated clusters (`cluster_hulls`).

## 3. Local Hardware & Virtual Environment Scope
- **Zero Cloud Requirement**: The system is designed to run 100% locally in a Python 3.12+ `.venv` with zero external cloud dependencies or paid API keys.
- **CPU-Only ML Inference**: Machine learning models (Logistic Regression, Random Forest, Isolation Forest) execute on CPU without requiring GPU acceleration. Feature extraction and batch classification for 1,000 accounts complete in < 2.5 seconds.
- **Disk Space Allocation**: Recommended disk space is at least 5GB for `data/snapshots/`, `data/exports/`, and `data/backups/`. Disk health probe alarms when free headroom drops below 500MB.

## 4. Privacy & PII Handling
- **PII Scrubbing**: By default, email addresses, phone numbers, and IPv4 addresses in scraped profiles are sanitized using HMAC-SHA256 pseudonymization (`sbh.security.anonymizer`).
- **Offline Air-Gapped Mode**: When `SBH_OFFLINE_MODE=1` is set, all external network sockets are strictly blocked, restricting analysis entirely to local archives and synthetic datasets.
