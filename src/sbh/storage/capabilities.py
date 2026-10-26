"""Persist the capability registry so the dashboard and API read one source of truth."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from sbh.contracts.capabilities import CapabilityRegistry
from sbh.shared import jsonutil
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database


def sync_registry(db: Database, registry: CapabilityRegistry, clock: Callable[[], datetime] = utcnow) -> int:
    now = iso_utc(clock())
    caps = registry.all()
    with db.transaction():
        db.executemany(
            "INSERT INTO platform_capabilities (platform, operation, collection_mode, status, supported, endpoint, "
            "api_version, required_scopes, requires_approval, pagination_notes, quota_notes, credentials_required, "
            "retention_notes, limitations, last_verified_at, verification_evidence, updated_at) "
            "VALUES (:p, :o, :m, :st, :sup, :ep, :av, :sc, :ra, :pn, :qn, :cr, :rn, :lim, :lv, :ve, :now) "
            "ON CONFLICT (platform, operation) DO UPDATE SET collection_mode = excluded.collection_mode, "
            "status = excluded.status, supported = excluded.supported, endpoint = excluded.endpoint, "
            "api_version = excluded.api_version, required_scopes = excluded.required_scopes, "
            "requires_approval = excluded.requires_approval, pagination_notes = excluded.pagination_notes, "
            "quota_notes = excluded.quota_notes, credentials_required = excluded.credentials_required, "
            "retention_notes = excluded.retention_notes, limitations = excluded.limitations, "
            "last_verified_at = excluded.last_verified_at, verification_evidence = excluded.verification_evidence, "
            "updated_at = excluded.updated_at",
            [{"p": c.platform.value, "o": c.operation.value, "m": c.mode.value, "st": c.status.value,
              "sup": c.supported, "ep": c.endpoint, "av": c.api_version,
              "sc": jsonutil.dumps(list(c.required_scopes)), "ra": c.requires_approval,
              "pn": c.pagination_notes, "qn": c.quota_notes,
              "cr": jsonutil.dumps(list(c.credentials_required)), "rn": c.retention_notes,
              "lim": jsonutil.dumps(list(c.limitations)),
              "lv": iso_utc(c.last_verified_at) if c.last_verified_at else None,
              "ve": c.verification_evidence, "now": now} for c in caps])
    return len(caps)
