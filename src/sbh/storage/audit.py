"""Audit trail storage and querying repository."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from sbh.shared import jsonutil
from sbh.shared.ids import new_id
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database

Clock = Callable[[], datetime]


class AuditRepository:
    def __init__(self, db: Database, clock: Clock = utcnow) -> None:
        self.db = db
        self.clock = clock

    def record(
        self,
        actor: str,
        action: str,
        subject_type: str,
        subject_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        event_id = new_id()
        now = iso_utc(self.clock())
        self.db.execute(
            "INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, subject_id, details) "
            "VALUES (:id, :now, :actor, :action, :st, :sid, :details)",
            {
                "id": event_id,
                "now": now,
                "actor": actor,
                "action": action,
                "st": subject_type,
                "sid": subject_id,
                "details": jsonutil.dumps(details or {}),
            },
        )
        return event_id

    def list_events(
        self,
        limit: int = 50,
        offset: int = 0,
        actor: str | None = None,
        action: str | None = None,
        subject_type: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses = []
        params: dict[str, Any] = {"lim": limit, "off": offset}
        if actor:
            clauses.append("actor = :actor")
            params["actor"] = actor
        if action:
            clauses.append("action = :action")
            params["action"] = action
        if subject_type:
            clauses.append("subject_type = :st")
            params["st"] = subject_type

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = (
            f"SELECT id, occurred_at, actor, action, subject_type, subject_id, details "
            f"FROM audit_events {where_clause} ORDER BY occurred_at DESC LIMIT :lim OFFSET :off"
        )
        rows = self.db.query_all(sql, params)
        for r in rows:
            r["details"] = jsonutil.loads(r["details"]) or {}
        return rows

    def count_events(
        self,
        actor: str | None = None,
        action: str | None = None,
        subject_type: str | None = None,
    ) -> int:
        clauses = []
        params: dict[str, Any] = {}
        if actor:
            clauses.append("actor = :actor")
            params["actor"] = actor
        if action:
            clauses.append("action = :action")
            params["action"] = action
        if subject_type:
            clauses.append("subject_type = :st")
            params["st"] = subject_type

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT COUNT(*) AS c FROM audit_events {where_clause}"
        row = self.db.query_one(sql, params)
        return int(row["c"]) if row else 0

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        row = self.db.query_one("SELECT * FROM audit_events WHERE id = :id", {"id": event_id})
        if row:
            row["details"] = jsonutil.loads(row["details"]) or {}
        return row
