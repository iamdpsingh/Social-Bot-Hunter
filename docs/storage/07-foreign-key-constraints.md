# Referential Integrity and Constraints

Foreign keys enforce edge validity: `relationship_edges` require existing source and target `platform_accounts`. Self-loops are strictly prohibited via `CHECK (source <> target)`.
