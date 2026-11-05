from __future__ import annotations

from tests.support import DbTestCase
from sbh.storage import EdgeRepository

class TestListRelationshipEdges(DbTestCase):
    def test_list_relationship_edges_empty(self) -> None:
        repo = EdgeRepository(self.db)
        edges, total = repo.list_relationship_edges("nonexistent_scan")
        assert edges == []
        assert total == 0
