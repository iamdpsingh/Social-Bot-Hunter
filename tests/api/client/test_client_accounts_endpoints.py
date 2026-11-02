from __future__ import annotations

import unittest
from services.api.client import ClientConfig, SocialBotHunterClient, SBHClientError, AuthenticationError


class ClientSdkTest_test_client_accounts_endpoints(unittest.TestCase):
    """test accounts client route paths."""

    def test_client_operation(self) -> None:
        with SocialBotHunterClient("http://testserver:8000") as client:
            self.assertEqual(client.config.base_url, "http://testserver:8000")
            self.assertTrue(issubclass(AuthenticationError, SBHClientError))
