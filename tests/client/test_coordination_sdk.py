"""Test CoordinationClient methods structure."""
from services.api.client.client import SocialBotHunterClient


def test_coordination_client_property():
    client = SocialBotHunterClient()
    assert hasattr(client, "coordination")
    assert client.coordination is not None
