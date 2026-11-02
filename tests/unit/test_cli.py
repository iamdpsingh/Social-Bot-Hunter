"""Unit tests for the SBH command line interface."""

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from sbh.cli import main
from sbh.config import load_config
from sbh.pipeline.run import import_dataset
from sbh.storage.scans import ScanRepository
from tests.support import DbTestCase, acct, manifest, post, write_dir

CFG = load_config()


class CliQuarantineTests(DbTestCase):
    def setUp(self):
        super().setUp()
        # Create a dirty dataset that triggers quarantine records while staying under max_invalid_fraction
        dirty_dir = write_dir(
            self.tmp / "dirty",
            man=manifest(),
            accounts=[acct(f"valid_{i}") for i in range(25)] + [
                acct("bad_follower", follower_count=-10),
                acct("bad_future", observed_at="2099-01-01T00:00:00Z"),
            ],
            content=[
                post("c1", "valid_0", "2026-09-15T12:00:00Z", "safe organic text"),
                post("c2", "valid_0", "invalid-time", "rejected post"),
            ],
        )
        self.res = import_dataset(self.db, dirty_dir, CFG)
        self.assertTrue(self.res.summary["quarantined_records"] >= 2)

    def test_quarantine_list_text(self):
        buf = io.StringIO()
        with mock.patch("sbh.cli._open", return_value=self.db), redirect_stdout(buf):
            code = main(["quarantine-list", self.res.scan_id])
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertIn(f"Quarantine summary for scan {self.res.scan_id}:", out)
        self.assertIn("Showing", out)

    def test_quarantine_list_json(self):
        buf = io.StringIO()
        with mock.patch("sbh.cli._open", return_value=self.db), redirect_stdout(buf):
            code = main(["quarantine-list", self.res.scan_id, "--json"])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertIn("summary", data)
        self.assertIn("records", data)
        self.assertGreaterEqual(len(data["records"]), 2)

    def test_quarantine_inspect_text_and_json(self):
        repo = ScanRepository(self.db)
        records = repo.list_quarantined_records(self.res.scan_id)
        self.assertTrue(records)
        target_id = records[0]["id"]

        # Text output
        buf_text = io.StringIO()
        with mock.patch("sbh.cli._open", return_value=self.db), redirect_stdout(buf_text):
            code = main(["quarantine-inspect", target_id])
        self.assertEqual(code, 0)
        self.assertIn(f"Quarantined Record: {target_id}", buf_text.getvalue())
        self.assertIn("Raw Payload:", buf_text.getvalue())

        # JSON output
        buf_json = io.StringIO()
        with mock.patch("sbh.cli._open", return_value=self.db), redirect_stdout(buf_json):
            code = main(["quarantine-inspect", target_id, "--json"])
        self.assertEqual(code, 0)
        rec = json.loads(buf_json.getvalue())
        self.assertEqual(rec["id"], target_id)
        self.assertEqual(rec["scan_id"], self.res.scan_id)

    def test_quarantine_inspect_nonexistent_returns_error(self):
        buf_err = io.StringIO()
        with mock.patch("sbh.cli._open", return_value=self.db), redirect_stderr(buf_err):
            code = main(["quarantine-inspect", "nonexistent-id-0000"])
        self.assertEqual(code, 1)
        self.assertIn("quarantined record not found", buf_err.getvalue())


if __name__ == "__main__":
    unittest.main()
