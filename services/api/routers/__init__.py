"""FastAPI route modules."""

from . import (
    accounts,
    adapters,
    audit,
    auth,
    capabilities,
    coordination,
    detection_ml,
    runtime,
    storage_mgmt,
    diff,
    health,
    imports,
    networks,
    scans,
    settings,
    users,
)

__all__ = [
    "accounts",
    "adapters",
    "audit",
    "auth",
    "capabilities",
    "coordination",
    "detection_ml",
    "runtime",
    "storage_mgmt",
    "diff",
    "health",
    "imports",
    "networks",
    "scans",
    "settings",
    "users",
]
