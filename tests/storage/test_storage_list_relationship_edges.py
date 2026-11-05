from __future__ import annotations

from sbh.storage import EdgeRepository
from tests.support import DbTestCase


class TestListRelationshipEdges(DbTestCase):
    def test_list_relationship_edges_empty(self) -> None:
        repo = EdgeRepository(self.db)
        edges, total = repo.list_relationship_edges("nonexistent_scan")
        assert edges == []
        assert total == 0
