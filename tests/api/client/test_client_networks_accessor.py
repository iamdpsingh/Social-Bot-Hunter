from __future__ import annotations

from services.api.client import SocialBotHunterClient
from services.api.client.networks import NetworksClient


def test_client_networks_property() -> None:
    client = SocialBotHunterClient(base_url="http://localhost:8080")
    assert hasattr(client, "networks")
    assert isinstance(client.networks, NetworksClient)
