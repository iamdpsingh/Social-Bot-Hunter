"""Test SettingsClient property initialization."""
from services.api.client.client import SocialBotHunterClient


def test_settings_client_property():
    client = SocialBotHunterClient()
    assert hasattr(client, "settings")
    assert client.settings is not None
