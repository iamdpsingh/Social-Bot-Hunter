"""Test DiffClient initialization on SDK."""
from services.api.client.client import SocialBotHunterClient


def test_diff_client_property():
    client = SocialBotHunterClient()
    assert hasattr(client, "diff")
    assert client.diff is not None
