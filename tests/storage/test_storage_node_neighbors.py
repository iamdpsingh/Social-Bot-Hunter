from __future__ import annotations

from sbh.storage.edges import EdgeRepository
from tests.support import DbTestCase


class TestStorageNodeNeighbors(DbTestCase):
    def test_get_node_neighbors_empty(self) -> None:
        repo = EdgeRepository(self.db)
        neighbors = repo.get_node_neighbors("s_none", "acc_none", direction="both")
        assert len(neighbors) == 0
