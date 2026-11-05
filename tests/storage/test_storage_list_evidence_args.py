from __future__ import annotations

from sbh.storage import AnalysisRepository
from tests.support import DbTestCase


class TestListEvidenceArgs(DbTestCase):
    def test_list_evidence_flexible_arity(self) -> None:
        repo = AnalysisRepository(self.db)
        assert repo.list_evidence("scan_1", "acc_1") == []
        assert repo.list_evidence("scan_1", "account", "acc_1") == []
