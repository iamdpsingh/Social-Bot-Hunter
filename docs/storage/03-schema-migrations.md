# Schema Migrations Protocol

Migrations are strictly versioned, sequentially applied, idempotent, and reversible. Each forward `.sql` migration is accompanied by a matching `.rollback.sql` script.
