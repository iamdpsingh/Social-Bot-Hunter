"""Asset manifest tracking and cryptographic tamper detection."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sbh.storage.fs import LocalStorageManager, StorageCategory, compute_sha256

MANIFEST_FILENAME = ".manifest.json"


@dataclass
class StorageAssetRecord:
    """Metadata record for a tracked storage asset."""

    asset_id: str
    category: str
    filename: str
    relative_path: str
    size_bytes: int
    sha256: str
    created_at: str
    modified_at: str
    is_protected: bool = False
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageAssetRecord:
        return cls(**data)


class AssetManifestManager:
    """Tracks and validates manifest records in storage directories."""

    def __init__(self, storage_manager: LocalStorageManager) -> None:
        self.storage = storage_manager
        self.manifest_path = self.storage.base_dir / MANIFEST_FILENAME
        self._records: dict[str, StorageAssetRecord] = {}
        self.load()

    def load(self) -> None:
        """Load manifest from disk if present."""
        if self.manifest_path.exists():
            try:
                data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                self._records = {k: StorageAssetRecord.from_dict(v) for k, v in data.get("assets", {}).items()}
            except (json.JSONDecodeError, OSError):
                self._records = {}
        else:
            self._records = {}

    def save(self) -> None:
        """Save manifest to disk atomically."""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now(UTC).isoformat(),
            "total_assets": len(self._records),
            "assets": {k: v.to_dict() for k, v in self._records.items()},
        }
        self.storage.base_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.manifest_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.manifest_path)

    def register_asset(
        self,
        category: StorageCategory,
        filename: str,
        is_protected: bool = False,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StorageAssetRecord:
        """Register or update an asset in manifest."""
        target = self.storage.safe_resolve(category, filename)
        if not target.exists():
            raise FileNotFoundError(f"Cannot register missing asset: {target}")

        stat = target.stat()
        digest = compute_sha256(target)
        asset_id = f"{category.value}:{filename}"
        now_str = datetime.now(UTC).isoformat()

        rec = StorageAssetRecord(
            asset_id=asset_id,
            category=category.value,
            filename=filename,
            relative_path=f"{category.value}/{filename}",
            size_bytes=stat.st_size,
            sha256=digest,
            created_at=now_str,
            modified_at=now_str,
            is_protected=is_protected,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._records[asset_id] = rec
        self.save()
        return rec

    def get_asset(self, asset_id: str) -> StorageAssetRecord | None:
        return self._records.get(asset_id)

    def list_assets(
        self,
        category: StorageCategory | None = None,
        tag: str | None = None,
        protected_only: bool = False,
    ) -> list[StorageAssetRecord]:
        """Query tracked assets with optional filters."""
        res: list[StorageAssetRecord] = []
        for rec in self._records.values():
            if category and rec.category != category.value:
                continue
            if tag and tag not in rec.tags:
                continue
            if protected_only and not rec.is_protected:
                continue
            res.append(rec)
        return res

    def mark_protected(self, asset_id: str, is_protected: bool = True) -> bool:
        """Mark an asset as protected from automated retention cleanup."""
        if asset_id in self._records:
            rec = self._records[asset_id]
            self._records[asset_id] = StorageAssetRecord(
                asset_id=rec.asset_id,
                category=rec.category,
                filename=rec.filename,
                relative_path=rec.relative_path,
                size_bytes=rec.size_bytes,
                sha256=rec.sha256,
                created_at=rec.created_at,
                modified_at=datetime.now(UTC).isoformat(),
                is_protected=is_protected,
                tags=rec.tags,
                metadata=rec.metadata,
            )
            self.save()
            return True
        return False

    def verify_tamper(self, asset_id: str) -> tuple[bool, str]:
        """Verify whether an asset matches its registered SHA-256 digest."""
        rec = self._records.get(asset_id)
        if not rec:
            return False, "Asset not tracked in manifest"

        cat = StorageCategory(rec.category)
        target = self.storage.safe_resolve(cat, rec.filename)
        if not target.exists():
            return False, "File missing from disk"

        current_digest = compute_sha256(target)
        if current_digest != rec.sha256:
            return False, f"Checksum mismatch: recorded={rec.sha256}, actual={current_digest}"

        return True, "Integrity verified"

    def remove_asset(self, asset_id: str) -> bool:
        """Remove record from manifest."""
        if asset_id in self._records:
            del self._records[asset_id]
            self.save()
            return True
        return False
