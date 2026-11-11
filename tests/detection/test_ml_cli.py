"""Unit tests for ML CLI commands."""

import unittest
from sbh.detection.ml.cli import main


class TestMLCLI(unittest.TestCase):
    def test_cli_info_command(self):
        ret = main(["info"])
        self.assertEqual(ret, 0)

    def test_cli_eval_command(self):
        ret = main(["eval"])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
