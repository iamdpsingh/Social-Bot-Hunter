"""Deterministic storage retention policy and pruning engine."""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from sbh.storage.fs import LocalStorageManager, StorageCategory
from sbh.storage.manifest import AssetManifestManager


@dataclass(frozen=True)
class RetentionPolicy:
    """Configurable retention thresholds for storage categories."""

    max_age_days: int | None = None
    max_directory_bytes: int | None = None
    keep_minimum_count: int = 3
    protected_tags: set[str] = field(default_factory=lambda: {"production", "baseline", "golden"})


@dataclass(frozen=True)
class PruneReport:
    """Report detailing reclaimed space and preserved assets after pruning."""

    category: str
    scanned_count: int
    deleted_count: int
    bytes_reclaimed: int
    preserved_count: int
    dry_run: bool
    deleted_files: list[str]
    errors: list[str]

    @property
    def reclaimed_mb(self) -> float:
        return round(self.bytes_reclaimed / (1024 * 1024), 2)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["reclaimed_mb"] = self.reclaimed_mb
        return d


class StorageRetentionEngine:
    """Enforces retention policies deterministically (LRU / oldest first)."""

    def __init__(
        self,
        storage_manager: LocalStorageManager,
        manifest_manager: AssetManifestManager | None = None,
    ) -> None:
        self.storage = storage_manager
        self.manifest = manifest_manager

    def prune_category(
        self,
        category: StorageCategory,
        policy: RetentionPolicy,
        dry_run: bool = False,
    ) -> PruneReport:
        """Prune assets in category matching age or capacity thresholds."""
        assets = self.storage.list_assets(category)
        scanned = len(assets)
        if scanned <= policy.keep_minimum_count:
            return PruneReport(
                category=category.value,
                scanned_count=scanned,
                deleted_count=0,
                bytes_reclaimed=0,
                preserved_count=scanned,
                dry_run=dry_run,
                deleted_files=[],
                errors=[],
            )

        now = time.time()
        # Sort oldest first (smallest modified_epoch)
        candidates = sorted(assets, key=lambda a: a.modified_epoch)
        to_delete: list[str] = []
        bytes_to_reclaim = 0
        preserved: list[str] = []
        errors: list[str] = []

        # Current total bytes in category
        current_total_bytes = sum(a.size_bytes for a in assets)

        for asset in candidates:
            # Enforce keep_minimum_count invariant
            remaining_count = scanned - len(to_delete)
            if remaining_count <= policy.keep_minimum_count:
                preserved.append(asset.filename)
                continue

            # Check protection in manifest
            asset_id = f"{category.value}:{asset.filename}"
            if self.manifest:
                rec = self.manifest.get_asset(asset_id)
                if rec and (rec.is_protected or any(t in policy.protected_tags for t in rec.tags)):
                    preserved.append(asset.filename)
                    continue

            should_delete = False

            # Check age limit
            if policy.max_age_days is not None:
                age_days = (now - asset.modified_epoch) / 86400.0
                if age_days > policy.max_age_days:
                    should_delete = True

            # Check directory size limit
            if policy.max_directory_bytes is not None:
                if (current_total_bytes - bytes_to_reclaim) > policy.max_directory_bytes:
                    should_delete = True

            if should_delete:
                to_delete.append(asset.filename)
                bytes_to_reclaim += asset.size_bytes
            else:
                preserved.append(asset.filename)

        deleted_actual: list[str] = []
        actual_reclaimed = 0

        if not dry_run:
            for fn in to_delete:
                try:
                    if self.storage.delete_asset(category, fn):
                        deleted_actual.append(fn)
                        if self.manifest:
                            self.manifest.remove_asset(f"{category.value}:{fn}")
                except OSError as exc:
                    errors.append(f"Failed to delete {fn}: {exc}")
            actual_reclaimed = bytes_to_reclaim
        else:
            deleted_actual = to_delete
            actual_reclaimed = bytes_to_reclaim

        return PruneReport(
            category=category.value,
            scanned_count=scanned,
            deleted_count=len(deleted_actual),
            bytes_reclaimed=actual_reclaimed,
            preserved_count=scanned - len(deleted_actual),
            dry_run=dry_run,
            deleted_files=deleted_actual,
            errors=errors,
        )

    def prune_all(
        self,
        policies: dict[StorageCategory, RetentionPolicy] | None = None,
        dry_run: bool = False,
    ) -> list[PruneReport]:
        """Prune all categories according to policies."""
        default_policy = RetentionPolicy(max_age_days=30, keep_minimum_count=3)
        reports: list[PruneReport] = []

        for cat in StorageCategory:
            pol = (policies or {}).get(cat, default_policy)
            reports.append(self.prune_category(cat, pol, dry_run=dry_run))

        return reports
