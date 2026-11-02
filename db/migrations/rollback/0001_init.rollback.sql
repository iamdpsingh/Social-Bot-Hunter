-- Social Bot Hunter: rollback script for 0001_init.sql
-- Drops all tables in reverse foreign key dependency order.
-- Portable SQL subset accepted by both SQLite and PostgreSQL.

DROP TABLE IF EXISTS audit_events;
DROP TABLE IF EXISTS platform_capabilities;
DROP TABLE IF EXISTS evidence_records;
DROP TABLE IF EXISTS cluster_memberships;
DROP TABLE IF EXISTS network_clusters;
DROP TABLE IF EXISTS risk_assessments;
DROP TABLE IF EXISTS account_features;
DROP TABLE IF EXISTS model_versions;
DROP TABLE IF EXISTS content_observations;
DROP TABLE IF EXISTS relationship_list_coverage;
DROP TABLE IF EXISTS relationship_edges;
DROP TABLE IF EXISTS account_observations;
DROP TABLE IF EXISTS platform_accounts;
DROP TABLE IF EXISTS quarantined_records;
DROP TABLE IF EXISTS scan_checkpoints;
DROP TABLE IF EXISTS dataset_imports;
DROP TABLE IF EXISTS scan_jobs;
