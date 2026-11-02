from __future__ import annotations

import unittest

from services.api.client import (
    AuthenticationError,
    SBHClientError,
    SocialBotHunterClient,
)


class ClientSdkTest_test_client_config_custom_url(unittest.TestCase):
    """test client custom base url."""

    def test_client_operation(self) -> None:
        with SocialBotHunterClient("http://testserver:8000") as client:
            self.assertEqual(client.config.base_url, "http://testserver:8000")
            self.assertTrue(issubclass(AuthenticationError, SBHClientError))
