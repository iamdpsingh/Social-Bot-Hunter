# Day 5 API Endpoints: Account Investigation & Follower Explorer

## Endpoints

### 1. `GET /api/v1/scans/{scan_id}/accounts`
Returns paginated account risk assessments.
- **Parameters**: `band`, `status`, `search`, `sort_by`, `limit`, `offset`.
- **Response**: `AccountListResponse`.

### 2. `GET /api/v1/scans/{scan_id}/accounts/{account_id}`
Returns profile observations, risk assessment, and calculated features for an account.
- **Response**: `AccountDetailResponse`.

### 3. `GET /api/v1/scans/{scan_id}/accounts/{account_id}/evidence`
Returns explainable indicator records and evidence trails.
- **Response**: `AccountEvidenceResponse`.

### 4. `GET /api/v1/scans/{scan_id}/relationships`
Returns paginated graph edges between observed accounts.
- **Parameters**: `relationship_type` (follower/following), `limit`, `offset`.
- **Response**: `RelationshipListResponse`.

### 5. `GET /api/v1/scans/{scan_id}/export/csv`
Streams RFC 4180 CSV export of accounts and risk scores.

### 6. `GET /api/v1/scans/{scan_id}/export/json`
Streams structured JSON export bundle.
