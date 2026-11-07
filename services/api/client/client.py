"""Unified SocialBotHunterClient SDK entrypoint."""

from __future__ import annotations

from services.api.client.accounts import AccountsClient
from services.api.client.audit import AuditClient
from services.api.client.auth import AuthClient
from services.api.client.capabilities import CapabilitiesClient
from services.api.client.config import ClientConfig
from services.api.client.coordination import CoordinationClient
from services.api.client.diff import DiffClient
from services.api.client.imports import ImportsClient
from services.api.client.networks import NetworksClient
from services.api.client.reports import ReportsClient
from services.api.client.scans import ScansClient
from services.api.client.session import ApiSession
from services.api.client.users import UsersClient


class SocialBotHunterClient:
    """Top-level client for Social Bot Hunter API."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.config = ClientConfig(base_url=base_url)
        self.session = ApiSession(self.config)
        self.auth = AuthClient(self.session)
        self.users = UsersClient(self.session)
        self.scans = ScansClient(self.session)
        self.accounts = AccountsClient(self.session)
        self.reports = ReportsClient(self.session)
        self.audit = AuditClient(self.session)
        self.capabilities = CapabilitiesClient(self.session)
        self.imports = ImportsClient(self.session)
        self.networks = NetworksClient(self.session)
        self.coordination = CoordinationClient(self.session)
        self.diff = DiffClient(self.session)

    def __enter__(self) -> SocialBotHunterClient:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass
