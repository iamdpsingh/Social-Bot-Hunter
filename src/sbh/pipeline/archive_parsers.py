"""Archive and dataset format parsers converting files to domain records."""

from __future__ import annotations

import csv
import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from sbh.detection.simhash import compute_simhash
from sbh.pipeline.archive_ingest import DatasetFormat, ExtractedArchive
from sbh.schemas.records import AccountObservationRecord, ContentRecord, QuarantinedRecord

class BaseArchiveParser(ABC):
    """Abstract base class for dataset archive parsers."""

    @abstractmethod
    def parse_content(self, target_path: Path) -> Iterator[ContentRecord | QuarantinedRecord]:
        """Stream content records or quarantined records from target path."""

    @abstractmethod
    def parse_accounts(self, target_path: Path) -> Iterator[AccountObservationRecord | QuarantinedRecord]:
        """Stream account observation records from target path."""


@dataclass
class IngestionBatchSummary:
    """Aggregated outcome of an archive parsing and ingestion operation."""
    archive_format: DatasetFormat
    accounts: list[AccountObservationRecord] = field(default_factory=list)
    content: list[ContentRecord] = field(default_factory=list)
    quarantined: list[QuarantinedRecord] = field(default_factory=list)
    elapsed_ms: float = 0.0
    total_records: int = 0
