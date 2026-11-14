# Platform Access & Capability Matrix

| Platform | Authentication Mechanism | Endpoints / Protocol | Rate Limits | Data Completeness | Offline Synthetic Fallback |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Twitter / X** | Bearer Token / OAuth 2.0 | REST API v2 (`/users`, `/tweets`) | 150 req / 15 min | Partial (Strict Graph Limits) | Yes (`generate-demo`) |
| **Bluesky** | AT Protocol Session Token | XRPC (`app.bsky.actor`, `feed`) | 3,000 req / 5 min | Full Public Graph | Yes (`generate-demo`) |
| **Mastodon** | App Access Token / Public | REST API v1 (`/accounts`, `/statuses`) | 300 req / 5 min | Full Instance Graph | Yes (`generate-demo`) |
| **Reddit** | OAuth 2.0 Script Client | Reddit Data API (`/user/about`, `/overview`) | 100 req / min | High (Public History) | Yes (`generate-demo`) |
| **YouTube** | Google API Key / OAuth 2.0 | YouTube Data API v3 (`channels`, `comments`) | 10,000 quota units / day | High (Public Channels) | Yes (`generate-demo`) |

## Operational Guidelines
- **Rate Limit Exhaustion**: When a platform adapter encounters HTTP 429, the system triggers exponential backoff with jitter up to 3 retries.
- **Air-Gapped Operation**: In air-gapped environments (`SBH_OFFLINE_MODE=1`), all live platform requests are bypassed in favor of local JSON/CSV archives or verified synthetic demo generators.
