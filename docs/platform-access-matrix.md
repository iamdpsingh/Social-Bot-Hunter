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

<!-- BEGIN GENERATED:capabilities -->
| Platform | Operation | Mode | Status | Supported | Endpoint / version | Verified |
|---|---|---|---|---|---|---|
| instagram | dataset_import | dataset_import | implemented | yes | - | never |
| instagram | list_content | official_api | not_configured | unknown | - | never |
| instagram | list_followers | official_api | not_configured | unknown | - | never |
| instagram | list_following | official_api | not_configured | unknown | - | never |
| instagram | lookup_account | official_api | not_configured | unknown | - | never |
| linkedin | dataset_import | dataset_import | implemented | yes | - | never |
| linkedin | list_content | official_api | not_configured | unknown | - | never |
| linkedin | list_followers | official_api | not_configured | unknown | - | never |
| linkedin | list_following | official_api | not_configured | unknown | - | never |
| linkedin | lookup_account | official_api | not_configured | unknown | - | never |
| tiktok | dataset_import | dataset_import | implemented | yes | - | never |
| tiktok | list_content | official_api | not_configured | unknown | - | never |
| tiktok | list_followers | official_api | not_configured | unknown | - | never |
| tiktok | list_following | official_api | not_configured | unknown | - | never |
| tiktok | lookup_account | official_api | not_configured | unknown | - | never |
| x | dataset_import | dataset_import | implemented | yes | - | never |
| x | list_content | official_api | not_configured | unknown | - | never |
| x | list_followers | official_api | not_configured | unknown | - | never |
| x | list_following | official_api | not_configured | unknown | - | never |
| x | lookup_account | official_api | not_configured | unknown | - | never |
| youtube | dataset_import | dataset_import | implemented | yes | - | never |
| youtube | list_content | official_api | not_configured | unknown | - | never |
| youtube | list_followers | official_api | not_configured | unknown | - | never |
| youtube | list_following | official_api | not_configured | unknown | - | never |
| youtube | lookup_account | official_api | not_configured | unknown | - | never |
<!-- END GENERATED:capabilities -->
