"""Client SDK configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClientConfig:
    """Configuration options for SocialBotHunterClient."""

    base_url: str = "http://localhost:8000"
    timeout_sec: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True
