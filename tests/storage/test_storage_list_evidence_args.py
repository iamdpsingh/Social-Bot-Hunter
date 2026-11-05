from __future__ import annotations

from sbh.storage import AnalysisRepository, Database

def test_list_evidence_flexible_arity() -> None:
    db = Database("sqlite:///:memory:")
    db.run_migrations()
    repo = AnalysisRepository(db)
    # Both 2-arg and 3-arg calls should succeed without TypeError
    assert repo.list_evidence("scan_1", "acc_1") == []
    assert repo.list_evidence("scan_1", "account", "acc_1") == []
