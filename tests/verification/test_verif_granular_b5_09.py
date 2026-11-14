"""Granular test 9: json round trip."""

from __future__ import annotations

import json
import unittest
from sbh.verification.matrix import AcceptanceMatrixGenerator


class TestVerifGranularB509(unittest.TestCase):
    def test_json_decoding(self):
        summary = AcceptanceMatrixGenerator.generate_summary()
        js = AcceptanceMatrixGenerator.to_json(summary)
        data = json.loads(js)
        self.assertEqual(len(data["criteria"]), 12)
        self.assertTrue(data["all_verified"])


if __name__ == "__main__":
    unittest.main()
