"""The data-quality checks required by the specification (section 7.2), one test each."""

import unittest
from dataclasses import replace
from datetime import UTC, datetime

from sbh.config import load_config
from sbh.schemas.validation import parse_manifest
from sbh.shared.errors import SchemaIncompatibleError
from tests.support import acct, edge, manifest
from tests.unit.test_validation import raw_of, reasons, run

CFG = load_config().imports
NOW = datetime(2026, 10, 1, tzinfo=UTC)


class SpecChecks(unittest.TestCase):
    def test_required_fields(self):
        self.assertIn("missing_required:observed_at", reasons(run([acct("a", observed_at="")])))

    def test_valid_identifiers(self):
        self.assertIn("invalid_identifier:platform_account_id", reasons(run([acct("a;DROP TABLE x")])))
        self.assertIn("invalid_identifier:platform_account_id", reasons(run([acct("x" * 129)])))

    def test_schema_compatibility(self):
        with self.assertRaises(SchemaIncompatibleError):
            parse_manifest(manifest(schema_version="9.0"), CFG, now=NOW)

    def test_duplicate_records(self):
        out = run([acct("a"), acct("a")])
        self.assertEqual(out.stats["exact_duplicates"]["account"], 1)

    def test_null_and_missingness_patterns_are_reported(self):
        out = run([acct(f"a{i}", follower_count="") for i in range(25)])
        self.assertEqual(out.stats["missing_fraction"]["follower_count"], 1.0)
        self.assertTrue(any("follower_count is missing in 100%" in w for w in out.warnings))

    def test_timestamp_validity(self):
        self.assertTrue(run([acct("a", observed_at="2026-13-45")]).quarantined)

    def test_non_negative_counts(self):
        for col in ("follower_count", "following_count", "post_count", "bio_length"):
            with self.subTest(col):
                self.assertTrue(any(r.startswith("negative_count") for r in reasons(run([acct("a", **{col: -3})]))))

    def test_relationship_direction_and_self_follow(self):
        out = run(relationships=[edge("a", "b"), edge("b", "a"), edge("c", "c")])
        self.assertEqual(len(out.relationships), 2)  # a->b and b->a stay distinct directed edges
        self.assertIn("self_relationship", reasons(out))

    def test_referential_integrity_endpoints_without_profile_are_flagged(self):
        out = run([acct("a")], [edge("a", "ghost1"), edge("a", "ghost2")])
        self.assertEqual(out.stats["stub_accounts"], 2)
        self.assertTrue(any("2 accounts appear only as" in w for w in out.warnings))

    def test_unexpected_row_count_change_is_not_checked_here_but_staleness_is(self):
        out = run([acct("a", observed_at="2026-01-01T00:00:00Z")])
        self.assertEqual(out.stats["stale_observations"], 1)
        self.assertTrue(any("older than 90 days" in w for w in out.warnings))

    def test_pagination_completeness_contradiction_downgrades_to_partial(self):
        ov = [{"platform_account_id": "a", "list_kind": "following", "completeness": "complete", "expected_count": 5}]
        out = run([acct("a")], [edge("a", "b"), edge("a", "c")],
                  relationship_coverage={"default": "unknown", "overrides": ov})
        self.assertEqual(out.coverage_overrides[("a", "following")].completeness.value, "partial")
        self.assertTrue(any("downgraded to partial" in w for w in out.warnings))

    def test_matching_expected_count_stays_complete(self):
        ov = [{"platform_account_id": "a", "list_kind": "following", "completeness": "complete", "expected_count": 2}]
        out = run([acct("a")], [edge("a", "b"), edge("a", "c")],
                  relationship_coverage={"default": "unknown", "overrides": ov})
        self.assertEqual(out.coverage_overrides[("a", "following")].completeness.value, "complete")

    def test_source_consistency_one_platform_per_dataset(self):
        out = run([acct("a", platform="instagram")], [edge("a", "b", platform="youtube")])
        self.assertEqual(reasons(out).count("platform_mismatch"), 2)

    def test_invalid_enum_values(self):
        self.assertIn("invalid_enum:relationship_type", reasons(run(relationships=[edge("a", "b", relationship_type="likes")])))
        with self.assertRaises(SchemaIncompatibleError):
            parse_manifest(manifest(collection_method="guess"), CFG, now=NOW)

    def test_configurable_thresholds_change_behaviour(self):
        raw = raw_of([acct(f"a{i}", follower_count="") for i in range(25)])
        from sbh.schemas.validation import validate_dataset
        m = parse_manifest(manifest(), CFG, now=NOW)
        strict = validate_dataset(raw, m, replace(CFG, missing_field_warn_fraction=0.5))
        lax = validate_dataset(raw, m, replace(CFG, missing_field_warn_fraction=1.01))
        self.assertTrue(strict.warnings)
        self.assertFalse(any("follower_count" in w for w in lax.warnings))

    def test_invalid_records_are_never_silently_discarded(self):
        rows = [acct("ok"), acct("bad", follower_count=-1), acct("ok"), acct("bad2", observed_at="x")]
        out = run(rows)
        self.assertEqual(len(out.accounts) + len(out.quarantined), len(rows))


if __name__ == "__main__":
    unittest.main()
