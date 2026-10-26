"""Baseline detection evaluation against labelled synthetic ground truth."""

import json
import unittest
from pathlib import Path

from sbh.config import load_config
from sbh.pipeline.run import import_dataset
from tests.support import DbTestCase

REPO = Path(__file__).resolve().parents[2]


class BaselineEvaluation(DbTestCase):
    def setUp(self):
        super().setUp()
        self.cfg = load_config()
        self.sample_dir = REPO / "data" / "samples" / "synthetic_demo"
        self.truth_file = REPO / "data" / "samples" / "synthetic_demo.truth.json"

    def test_evaluate_rules_baseline_against_ground_truth(self):
        truth = json.loads(self.truth_file.read_text(encoding="utf-8"))
        bot_accounts = set(truth["ring_obvious"] + truth["ring_stealth"])
        organic_accounts = set(truth["organic"] + truth["friends"])

        res = import_dataset(self.db, self.sample_dir, self.cfg)
        self.assertIn(res.status, ("complete", "partial"))

        rows = self.db.query_all(
            """
            SELECT pa.platform_account_id, ra.score, ra.band, ra.status
            FROM risk_assessments ra
            JOIN platform_accounts pa ON pa.id = ra.platform_account_id
            WHERE ra.scan_id = :scan_id
            """,
            {"scan_id": res.scan_id},
        )
        scores = {r["platform_account_id"]: r for r in rows if r["status"] == "scored"}

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        # High risk threshold >= 50 (elevated or strong combination of indicators)
        for bot_id in bot_accounts:
            assessment = scores.get(bot_id)
            if assessment and assessment["score"] is not None and assessment["score"] >= 50.0:
                tp += 1
            else:
                fn += 1

        for org_id in organic_accounts:
            assessment = scores.get(org_id)
            if assessment and assessment["score"] is not None and assessment["score"] >= 50.0:
                fp += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Assert baseline requirements on synthetic benchmark:
        # All 10 planted ring accounts must be detected with elevated or strong indicators (recall = 1.0)
        self.assertEqual(tp, 10)
        self.assertEqual(fn, 0)
        self.assertEqual(recall, 1.0)

        # Organic and friend group accounts must not receive elevated/strong scores (fp = 0)
        self.assertEqual(fp, 0)
        self.assertEqual(precision, 1.0)
        self.assertEqual(f1, 1.0)


if __name__ == "__main__":
    unittest.main()
