"""Platform contracts public exports."""

from .adapter import AccessOutcome, Page, PlatformAdapter
from .capabilities import Capability, CapabilityStatus, Operation, default_registry
from .platforms import Platform

__all__ = [
    "Platform",
    "PlatformAdapter",
    "AccessOutcome",
    "Page",
    "Capability",
    "CapabilityStatus",
    "Operation",
    "default_registry",
]
