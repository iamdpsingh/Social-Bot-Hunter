# Social Bot Hunter - Database Schema & Data Dictionary

This document details the relational database tables, columns, indexes, and constraints implemented in SQLite and PostgreSQL.

## 1. Table: `scans`
Stores top-level investigation scan sessions.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `scan_id` | `VARCHAR(36)` | `PRIMARY KEY` | Unique UUID v4 identifying the scan session |
| `platform` | `VARCHAR(32)` | `NOT NULL` | Social media platform identifier (`x`, `bluesky`, etc.) |
| `status` | `VARCHAR(32)` | `NOT NULL` | Execution status (`queued`, `running`, `completed`, `failed`) |
| `config_version` | `VARCHAR(32)` | `NOT NULL` | Detection rules configuration version (`rules-v1`) |
| `completeness` | `VARCHAR(32)` | `NOT NULL` | Data completeness score (`full`, `partial`, `sparse`) |
| `actor` | `VARCHAR(64)` | `NOT NULL` | User or automated service initiating the scan |
| `created_at` | `TIMESTAMP` | `NOT NULL` | ISO 8601 UTC creation timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | Last state modification timestamp |

## 2. Table: `platform_accounts`
Stores unique social media accounts observed across scans.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `platform_account_id` | `VARCHAR(64)` | `PRIMARY KEY` | Platform-specific account identifier |
| `platform` | `VARCHAR(32)` | `NOT NULL` | Platform name |
| `handle` | `VARCHAR(128)` | `NOT NULL` | Account screen name / username |
| `display_name` | `VARCHAR(256)` | `NULLABLE` | Display name formatted by user |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Account creation timestamp |

## 3. Table: `account_observations`
Stores point-in-time profile metadata and bot-risk assessments.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `observation_id` | `VARCHAR(36)` | `PRIMARY KEY` | Unique observation UUID |
| `scan_id` | `VARCHAR(36)` | `FOREIGN KEY (scans)` | Associated scan session |
| `platform_account_id`| `VARCHAR(64)`| `FOREIGN KEY (platform_accounts)` | Subject account |
| `risk_score` | `REAL` | `NOT NULL` | Computed bot score (0.0 to 1.0) |
| `risk_category` | `VARCHAR(32)` | `NOT NULL` | Classification (`bot`, `suspicious`, `human`) |
| `followers_count` | `INTEGER` | `NOT NULL` | Observed followers count |
| `following_count` | `INTEGER` | `NOT NULL` | Observed following count |
| `post_count` | `INTEGER` | `NOT NULL` | Lifetime post count |
| `simhash_64` | `VARCHAR(16)` | `NULLABLE` | 64-bit hexadecimal SimHash of recent posts |

## 4. Table: `coordination_campaigns`
Stores detected candidate coordinated inauthentic behavior clusters.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `campaign_id` | `VARCHAR(36)` | `PRIMARY KEY` | Unique campaign UUID |
| `scan_id` | `VARCHAR(36)` | `FOREIGN KEY (scans)` | Associated scan session |
| `coordination_type` | `VARCHAR(64)` | `NOT NULL` | Type (`simhash_cluster`, `burst_synchronicity`, `dense_clique`) |
| `cluster_size` | `INTEGER` | `NOT NULL` | Number of member accounts |
| `confidence` | `REAL` | `NOT NULL` | Coordination confidence score (0.0 to 1.0) |
