"""Storage protocol contracts package."""

from __future__ import annotations

from sbh.storage.protocols.accounts import AccountStoreProtocol
from sbh.storage.protocols.audit import AuditStoreProtocol
from sbh.storage.protocols.base import BaseRepositoryProtocol
from sbh.storage.protocols.checkpoint import CheckpointStoreProtocol
from sbh.storage.protocols.communities import CommunityStoreProtocol
from sbh.storage.protocols.content import ContentStoreProtocol
from sbh.storage.protocols.features import FeatureStoreProtocol
from sbh.storage.protocols.health import StorageHealthProtocol
from sbh.storage.protocols.pooling import ConnectionPoolProtocol
from sbh.storage.protocols.quarantine import QuarantineStoreProtocol
from sbh.storage.protocols.relationships import RelationshipStoreProtocol
from sbh.storage.protocols.reports import ReportStoreProtocol
from sbh.storage.protocols.scans import ScanStoreProtocol
from sbh.storage.protocols.transactions import TransactionProtocol
from sbh.storage.protocols.users import UserStoreProtocol

__all__ = [
    "AccountStoreProtocol",
    "AuditStoreProtocol",
    "BaseRepositoryProtocol",
    "CheckpointStoreProtocol",
    "CommunityStoreProtocol",
    "ConnectionPoolProtocol",
    "ContentStoreProtocol",
    "FeatureStoreProtocol",
    "QuarantineStoreProtocol",
    "RelationshipStoreProtocol",
    "ReportStoreProtocol",
    "ScanStoreProtocol",
    "StorageHealthProtocol",
    "TransactionProtocol",
    "UserStoreProtocol",
]
