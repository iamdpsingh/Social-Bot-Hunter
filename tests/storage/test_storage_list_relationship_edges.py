from __future__ import annotations

from sbh.storage import Database, EdgeRepository

def test_list_relationship_edges_empty() -> None:
    db = Database("sqlite:///:memory:")
    db.run_migrations()
    repo = EdgeRepository(db)
    edges, total = repo.list_relationship_edges("nonexistent_scan")
    assert edges == []
    assert total == 0
