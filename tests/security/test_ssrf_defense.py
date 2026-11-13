"""Tests verifying outbound URL validation rejects private IP ranges and cloud metadata."""

from __future__ import annotations

import ipaddress
import unittest
from urllib.parse import urlparse


def is_url_safe_for_outbound_fetch(target_url: str) -> bool:
    """Validate that target_url does not resolve to internal or cloud-metadata IPs."""
    parsed = urlparse(target_url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except ValueError:
        # Domain name, check blacklist keywords
        if host.lower() in {"localhost", "127.0.0.1", "metadata.google.internal"}:
            return False
    return True


class TestSSRFDefense(unittest.TestCase):
    def test_reject_cloud_metadata(self) -> None:
        self.assertFalse(is_url_safe_for_outbound_fetch("http://169.254.169.254/latest/meta-data/"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://metadata.google.internal/computeMetadata/v1/"))

    def test_reject_loopback_and_private_ips(self) -> None:
        self.assertFalse(is_url_safe_for_outbound_fetch("http://127.0.0.1:8000/internal"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://localhost:3000"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://10.0.0.5:8080/data"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://192.168.1.1/admin"))

    def test_allow_public_urls(self) -> None:
        self.assertTrue(is_url_safe_for_outbound_fetch("https://api.twitter.com/2/users"))
        self.assertTrue(is_url_safe_for_outbound_fetch("https://graph.facebook.com/v19.0"))


if __name__ == "__main__":
    unittest.main()
