"""Scan lifecycle, checkpoints, dataset imports, quarantine and audit trail."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any

from sbh.schemas.records import QuarantinedRecord
from sbh.shared import jsonutil
from sbh.shared.errors import InvalidTransitionError
from sbh.shared.ids import new_id
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database

# Allowed scan state machine. Terminal states have no outgoing edges except failed -> running,
# which is how an operator resumes an interrupted scan from its checkpoints.
ALLOWED: dict[str, frozenset[str]] = {
    "pending": frozenset({"running", "cancelled", "failed", "awaiting_access_approval"}),
    "awaiting_access_approval": frozenset({"running", "cancelled"}),
    "running": frozenset({"complete", "partial", "failed", "cancelled"}),
    "failed": frozenset({"running"}),
    "complete": frozenset(),
    "partial": frozenset(),
    "cancelled": frozenset(),
}
TERMINAL = frozenset({"complete", "partial", "failed", "cancelled"})

Clock = Callable[[], datetime]


class ScanRepository:
    def __init__(self, db: Database, clock: Clock = utcnow) -> None:
        self.db = db
        self.clock = clock

    # ---- lifecycle
    def create_scan(
        self, *, scan_type: str, collection_mode: str, platform: str, data_origin: str,
        requested_by: str, reference_time: datetime, config_version: str, config_sha256: str,
    ) -> str:
        scan_id = new_id()
        self.db.execute(
            "INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, "
            "requested_by, created_at, reference_time, config_version, config_sha256, status_detail) "
            "VALUES (:id, :scan_type, :mode, :platform, 'pending', :origin, :by, :now, :ref, :cv, :cs, '{}')",
            {"id": scan_id, "scan_type": scan_type, "mode": collection_mode, "platform": platform,
             "origin": data_origin, "by": requested_by, "now": iso_utc(self.clock()),
             "ref": iso_utc(reference_time), "cv": config_version, "cs": config_sha256},
        )
        return scan_id

    def get_scan(self, scan_id: str) -> dict[str, Any] | None:
        row = self.db.query_one("SELECT * FROM scan_jobs WHERE id = :id", {"id": scan_id})
        if row:
            row["status_detail"] = jsonutil.loads(row["status_detail"]) or {}
        return row

    def transition(
        self, scan_id: str, to: str, allowed_from: Sequence[str], *,
        failure_reason: str | None = None, completeness: str | None = None,
    ) -> None:
        """Atomically change scan status. The UPDATE is conditional on the current status, so two
        workers cannot both win a transition."""
        for src in allowed_from:
            if to not in ALLOWED[src]:
                raise ValueError(f"programming error: {src} -> {to} is not a valid transition")
        now = iso_utc(self.clock())
        params: dict[str, Any] = {"id": scan_id, "to": to, "now": now, "reason": failure_reason,
                                  "comp": completeness}
        placeholders = ", ".join(f":f{i}" for i in range(len(allowed_from)))
        params.update({f"f{i}": s for i, s in enumerate(allowed_from)})
        finishing = to in TERMINAL
        changed = self.db.execute(
            "UPDATE scan_jobs SET status = :to, "
            "started_at = CASE WHEN :to = 'running' AND started_at IS NULL THEN :now ELSE started_at END, "
            f"finished_at = {':now' if finishing else 'NULL'}, "
            "failure_reason = :reason, "
            "collection_completeness = COALESCE(:comp, collection_completeness) "
            f"WHERE id = :id AND status IN ({placeholders})",
            params,
        )
        if changed == 0:
            current = self.db.query_one("SELECT status FROM scan_jobs WHERE id = :id", {"id": scan_id})
            raise InvalidTransitionError(
                f"scan {scan_id}: cannot move to {to!r} from {current['status'] if current else 'missing'!r}"
            )

    def merge_detail(self, scan_id: str, patch: dict[str, Any]) -> None:
        with self.db.transaction():
            row = self.db.query_one("SELECT status_detail FROM scan_jobs WHERE id = :id", {"id": scan_id})
            detail = jsonutil.loads(row["status_detail"]) if row else {}
            detail.update(patch)
            self.db.execute("UPDATE scan_jobs SET status_detail = :d WHERE id = :id",
                            {"d": jsonutil.dumps(detail), "id": scan_id})

    def list_scans(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.db.query_all("SELECT * FROM scan_jobs ORDER BY created_at DESC LIMIT :n", {"n": limit})
        for r in rows:
            r["status_detail"] = jsonutil.loads(r["status_detail"]) or {}
        return rows

    # ---- checkpoints
    def set_checkpoint(self, scan_id: str, stage: str, cursor: int, done: bool) -> None:
        self.db.execute(
            "INSERT INTO scan_checkpoints (scan_id, stage, cursor_pos, status, updated_at) "
            "VALUES (:s, :stage, :c, :st, :now) "
            "ON CONFLICT (scan_id, stage) DO UPDATE SET cursor_pos = excluded.cursor_pos, "
            "status = excluded.status, updated_at = excluded.updated_at",
            {"s": scan_id, "stage": stage, "c": cursor, "st": "done" if done else "in_progress",
             "now": iso_utc(self.clock())},
        )

    def get_checkpoint(self, scan_id: str, stage: str) -> tuple[int, bool] | None:
        row = self.db.query_one(
            "SELECT cursor_pos, status FROM scan_checkpoints WHERE scan_id = :s AND stage = :st",
            {"s": scan_id, "st": stage},
        )
        return (int(row["cursor_pos"]), row["status"] == "done") if row else None

    # ---- quarantine
    def add_quarantine(self, scan_id: str, records: Sequence[QuarantinedRecord]) -> None:
        now = iso_utc(self.clock())
        self.db.executemany(
            "INSERT INTO quarantined_records (id, scan_id, entity, source_ref, kind, reasons, raw, created_at) "
            "VALUES (:id, :s, :e, :ref, :k, :r, :raw, :now) "
            "ON CONFLICT (scan_id, entity, source_ref) DO NOTHING",
            [{"id": new_id(), "s": scan_id, "e": q.entity, "ref": q.source_ref, "k": q.kind,
              "r": jsonutil.dumps(list(q.reasons)), "raw": jsonutil.dumps(q.raw), "now": now}
             for q in records],
        )

    def quarantine_summary(self, scan_id: str) -> list[dict[str, Any]]:
        return self.db.query_all(
            "SELECT entity, kind, COUNT(*) AS n FROM quarantined_records WHERE scan_id = :s "
            "GROUP BY entity, kind ORDER BY entity, kind", {"s": scan_id})

    # ---- dataset imports
    def create_dataset_import(
        self, *, scan_id: str, dataset_name: str, source_name: str, sha256: str,
        schema_version: str, collection_method: str, source_description: str,
        is_synthetic: bool, manifest: dict[str, Any],
    ) -> str:
        imp = new_id()
        self.db.execute(
            "INSERT INTO dataset_imports (id, scan_id, dataset_name, source_name, content_sha256, "
            "schema_version, collection_method, source_description, is_synthetic, manifest, "
            "record_counts, imported_at) VALUES (:id, :s, :n, :src, :sha, :v, :m, :d, :syn, :man, '{}', :now)",
            {"id": imp, "s": scan_id, "n": dataset_name, "src": source_name, "sha": sha256,
             "v": schema_version, "m": collection_method, "d": source_description,
             "syn": is_synthetic, "man": jsonutil.dumps(manifest), "now": iso_utc(self.clock())},
        )
        return imp

    def set_record_counts(self, scan_id: str, counts: dict[str, Any]) -> None:
        self.db.execute("UPDATE dataset_imports SET record_counts = :c WHERE scan_id = :s",
                        {"c": jsonutil.dumps(counts), "s": scan_id})

    def find_dataset_import(self, sha256: str) -> dict[str, Any] | None:
        return self.db.query_one("SELECT * FROM dataset_imports WHERE content_sha256 = :h", {"h": sha256})

    def previous_import(self, dataset_name: str, platform: str, exclude_scan: str) -> dict[str, Any] | None:
        row = self.db.query_one(
            "SELECT d.*, s.platform FROM dataset_imports d JOIN scan_jobs s ON s.id = d.scan_id "
            "WHERE d.dataset_name = :n AND s.platform = :p AND d.scan_id <> :x "
            "AND s.status IN ('complete', 'partial') ORDER BY d.imported_at DESC LIMIT 1",
            {"n": dataset_name, "p": platform, "x": exclude_scan},
        )
        if row:
            row["record_counts"] = jsonutil.loads(row["record_counts"]) or {}
        return row

    # ---- audit
    def audit(self, actor: str, action: str, subject_type: str, subject_id: str | None,
              details: dict[str, Any] | None = None) -> None:
        self.db.execute(
            "INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, subject_id, details) "
            "VALUES (:id, :now, :a, :act, :st, :sid, :d)",
            {"id": new_id(), "now": iso_utc(self.clock()), "a": actor, "act": action,
             "st": subject_type, "sid": subject_id, "d": jsonutil.dumps(details or {})},
        )
