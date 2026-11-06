from __future__ import annotations

from sbh.storage.edges import EdgeRepository
from tests.support import DbTestCase


class TestStorageCountGraphEdges(DbTestCase):
    def test_count_graph_edges(self) -> None:
        repo = EdgeRepository(self.db)
        total = repo.count_graph_edges("s_empty")
        assert total == 0
