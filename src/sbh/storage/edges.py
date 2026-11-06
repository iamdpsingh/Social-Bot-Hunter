"""Directed relationship edges and list-coverage records."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sbh.schemas.records import RelationshipRecord
from sbh.shared.ids import new_id
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database


@dataclass(frozen=True)
class CoverageRow:
    platform_account_id: str  # internal id when writing, public id when read back
    list_kind: str
    completeness: str
    observed_count: int
    expected_count: int | None


class EdgeRepository:
    def __init__(self, db: Database, clock: Callable[[], datetime] = utcnow) -> None:
        self.db = db
        self.clock = clock

    def insert_edges(
        self,
        scan_id: str,
        collected_at: datetime,
        provenance: str,
        records: Sequence[RelationshipRecord],
        id_map: dict[str, str],
    ) -> None:
        self.db.executemany(
            "INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, "
            "relationship_type, observed_at, collected_at, verification_status, provenance) "
            "VALUES (:id, :scan, :platform, :src, :dst, :type, :obs, :col, :vs, :prov) "
            "ON CONFLICT (scan_id, source_account_id, target_account_id, relationship_type) DO NOTHING",
            [
                {
                    "id": new_id(),
                    "scan": scan_id,
                    "platform": r.platform,
                    "src": id_map[r.source_account_id],
                    "dst": id_map[r.target_account_id],
                    "type": r.relationship_type.value,
                    "obs": iso_utc(r.observed_at),
                    "col": iso_utc(collected_at),
                    "vs": r.verification_status.value,
                    "prov": provenance,
                }
                for r in records
            ],
        )

    def insert_coverage(self, scan_id: str, rows: Sequence[CoverageRow]) -> None:
        self.db.executemany(
            "INSERT INTO relationship_list_coverage (scan_id, platform_account_id, list_kind, completeness, "
            "observed_count, expected_count) VALUES (:s, :a, :k, :c, :o, :e) "
            "ON CONFLICT (scan_id, platform_account_id, list_kind) DO UPDATE SET "
            "completeness = excluded.completeness, observed_count = excluded.observed_count, "
            "expected_count = excluded.expected_count",
            [
                {
                    "s": scan_id,
                    "a": r.platform_account_id,
                    "k": r.list_kind,
                    "c": r.completeness,
                    "o": r.observed_count,
                    "e": r.expected_count,
                }
                for r in rows
            ],
        )

    def load_edges(self, scan_id: str) -> list[tuple[str, str]]:
        """(source public id, target public id) pairs observed in the scan, directed."""
        rows = self.db.query_all(
            "SELECT s.platform_account_id AS src, t.platform_account_id AS dst FROM relationship_edges e "
            "JOIN platform_accounts s ON s.id = e.source_account_id "
            "JOIN platform_accounts t ON t.id = e.target_account_id "
            "WHERE e.scan_id = :s ORDER BY src, dst",
            {"s": scan_id},
        )
        return [(r["src"], r["dst"]) for r in rows]

    def load_coverage(self, scan_id: str) -> dict[tuple[str, str], CoverageRow]:
        rows = self.db.query_all(
            "SELECT a.platform_account_id AS pid, c.list_kind, c.completeness, c.observed_count, "
            "c.expected_count FROM relationship_list_coverage c "
            "JOIN platform_accounts a ON a.id = c.platform_account_id WHERE c.scan_id = :s",
            {"s": scan_id},
        )
        return {
            (r["pid"], r["list_kind"]): CoverageRow(
                r["pid"],
                r["list_kind"],
                r["completeness"],
                r["observed_count"],
                r["expected_count"],
            )
            for r in rows
        }

    def count_edges(self, scan_id: str) -> int:
        row = self.db.query_one(
            "SELECT COUNT(*) AS n FROM relationship_edges WHERE scan_id = :s", {"s": scan_id}
        )
        return int(row["n"]) if row else 0

    def list_relationship_edges(
        self,
        scan_id: str,
        relationship_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        query = (
            "SELECT s.platform_account_id AS source_account_id, "
            "t.platform_account_id AS target_account_id, "
            "e.relationship_type, e.observed_at "
            "FROM relationship_edges e "
            "JOIN platform_accounts s ON s.id = e.source_account_id "
            "JOIN platform_accounts t ON t.id = e.target_account_id "
            "WHERE e.scan_id = :s"
        )
        params: dict[str, Any] = {"s": scan_id}
        if relationship_type:
            query += " AND e.relationship_type = :type"
            params["type"] = relationship_type

        count_query = (
            "SELECT COUNT(*) AS total FROM relationship_edges WHERE scan_id = :s"
        )
        if relationship_type:
            count_query += " AND relationship_type = :type"

        total_row = self.db.query_one(count_query, params)
        total = int(total_row["total"]) if total_row else 0

        query += " ORDER BY e.observed_at DESC, e.id DESC LIMIT :limit OFFSET :offset"
        query_params = dict(params)
        query_params["limit"] = limit
        query_params["offset"] = offset

        rows = self.db.query_all(query, query_params)
        return rows, total

    def get_node_neighbors(
        self,
        scan_id: str,
        platform_account_id: str,
        direction: str = "both",
    ) -> list[dict[str, Any]]:
        """Retrieve 1-hop neighbor records for a specific platform account."""
        results: list[dict[str, Any]] = []

        if direction in ("out", "both"):
            out_rows = self.db.query_all(
                "SELECT t.platform_account_id AS neighbor_id, 'outbound' AS direction, "
                "e.relationship_type, e.observed_at "
                "FROM relationship_edges e "
                "JOIN platform_accounts s ON s.id = e.source_account_id "
                "JOIN platform_accounts t ON t.id = e.target_account_id "
                "WHERE e.scan_id = :s AND s.platform_account_id = :p",
                {"s": scan_id, "p": platform_account_id},
            )
            results.extend(out_rows)

        if direction in ("in", "both"):
            in_rows = self.db.query_all(
                "SELECT s.platform_account_id AS neighbor_id, 'inbound' AS direction, "
                "e.relationship_type, e.observed_at "
                "FROM relationship_edges e "
                "JOIN platform_accounts s ON s.id = e.source_account_id "
                "JOIN platform_accounts t ON t.id = e.target_account_id "
                "WHERE e.scan_id = :s AND t.platform_account_id = :p",
                {"s": scan_id, "p": platform_account_id},
            )
            results.extend(in_rows)

        return results

    def count_graph_edges(self, scan_id: str) -> int:
        """Return total count of directed edges for a scan graph."""
        row = self.db.query_one(
            "SELECT COUNT(*) AS total FROM relationship_edges WHERE scan_id = :s",
            {"s": scan_id},
        )
        return int(row["total"]) if row else 0

