import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from sbh.config import load_config
from sbh.schemas.io import EXTRA_KEY, RawDataset, RawRow, load_source
from sbh.schemas.records import Completeness
from sbh.schemas.validation import parse_manifest, validate_dataset
from sbh.shared.errors import ImportLimitError, SchemaIncompatibleError
from tests.support import acct, edge, manifest, post, write_dir

CFG = load_config().imports
NOW = datetime(2026, 10, 1, tzinfo=UTC)


def raw_of(accounts=(), relationships=(), content=()):
    ds = RawDataset("t", "x" * 64, {})
    for entity, rows in (("accounts", accounts), ("relationships", relationships), ("content", content)):
        ds.rows[entity] = [RawRow(f"{entity}:{i}", dict(r)) for i, r in enumerate(rows, start=2)]
    return ds


def run(accounts=(), relationships=(), content=(), **man):
    m = parse_manifest(manifest(**man), CFG, now=NOW)
    return validate_dataset(raw_of(accounts, relationships, content), m, CFG)


def reasons(out):
    return [r for q in out.quarantined for r in q.reasons]


class ManifestTests(unittest.TestCase):
    def test_valid_manifest(self):
        m = parse_manifest(manifest(), CFG, now=NOW)
        self.assertEqual((m.platform, m.coverage_default), ("x", Completeness.COMPLETE))
        self.assertTrue(m.is_synthetic)

    def test_each_problem_is_reported(self):
        bad = manifest(platform="myspace", collected_at="2099-01-01T00:00:00Z", collection_method="scraped")
        del bad["source_description"]
        with self.assertRaises(SchemaIncompatibleError) as ctx:
            parse_manifest(bad, CFG, now=NOW)
        msg = str(ctx.exception)
        for needle in ("platform", "collected_at", "collection_method", "source_description"):
            self.assertIn(needle, msg)

    def test_unsupported_major_version_rejected(self):
        with self.assertRaisesRegex(SchemaIncompatibleError, "unsupported schema_version"):
            parse_manifest(manifest(schema_version="2.0"), CFG, now=NOW)

    def test_minor_versions_accepted(self):
        parse_manifest(manifest(schema_version="1.7"), CFG, now=NOW)

    def test_conflicting_coverage_declarations_rejected(self):
        ov = [{"platform_account_id": "a", "list_kind": "following", "completeness": "complete"},
              {"platform_account_id": "a", "list_kind": "following", "completeness": "partial"}]
        with self.assertRaisesRegex(SchemaIncompatibleError, "conflicting duplicate"):
            parse_manifest(manifest(relationship_coverage={"default": "unknown", "overrides": ov}), CFG, now=NOW)


class AccountRowTests(unittest.TestCase):
    def test_missing_is_none_and_zero_is_zero(self):
        out = run([acct("a", follower_count="", following_count="0", has_bio="", has_profile_image="false")])
        a = out.accounts[0]
        self.assertIsNone(a.follower_count)
        self.assertEqual(a.following_count, 0)
        self.assertIsNone(a.has_bio)
        self.assertIs(a.has_profile_image, False)

    def test_every_fault_is_quarantined_with_a_reason(self):
        cases = {
            "negative_count:follower_count": acct("a", follower_count=-1),
            "invalid_integer:post_count": acct("a", post_count="12.5"),
            "invalid_boolean:has_bio": acct("a", has_bio="maybe"),
            "missing_required:platform_account_id": acct(""),
            "invalid_identifier:platform_account_id": acct("has space"),
            "invalid_platform": acct("a", platform="myspace"),
            "platform_mismatch": acct("a", platform="tiktok"),
            "future_timestamp:observed_at": acct("a", observed_at="2099-01-01T00:00:00Z"),
            "inconsistent:account_created_after_observation": acct("a", account_created_at="2026-10-01T00:00:00Z"),
            "inconsistent:has_bio_false_with_bio_length": acct("a", has_bio="false", bio_length=40),
        }
        for expected, row in cases.items():
            with self.subTest(expected):
                out = run([row])
                self.assertEqual(out.accounts, [])
                self.assertTrue(any(r.startswith(expected) for r in reasons(out)), reasons(out))

    def test_timestamp_problems(self):
        for bad in ("yesterday", "2026-09-30T10:00:00", "1999-01-01T00:00:00Z", ""):
            with self.subTest(bad):
                out = run([acct("a", observed_at=bad)])
                self.assertEqual(len(out.quarantined), 1)

    def test_multiple_problems_in_one_row_are_all_listed(self):
        out = run([acct("a", follower_count=-1, has_bio="maybe")])
        self.assertEqual(len(out.quarantined[0].reasons), 2)

    def test_normalisation(self):
        out = run([acct("0042", username="@maya", has_bio="", bio_length=12, display_name="Maya", has_display_name="")])
        a = out.accounts[0]
        self.assertEqual((a.platform_account_id, a.username), ("0042", "maya"))  # id kept as text, @ removed
        self.assertIs(a.has_bio, True)            # derived from bio_length > 0
        self.assertIs(a.has_display_name, True)   # derived from display_name

    def test_exact_and_conflicting_duplicates(self):
        row = acct("a")
        out = run([row, dict(row), {**row, "follower_count": 7}])
        self.assertEqual(len(out.accounts), 1)
        kinds = sorted((q.kind, q.reasons[0]) for q in out.quarantined)
        self.assertEqual(kinds, [("duplicate", "duplicate_in_file"), ("invalid", "conflicting_duplicate")])
        self.assertEqual(out.rejected_count, 1)  # only the conflicting one counts as rejected

    def test_malformed_extra_cells_quarantined(self):
        ds = raw_of([acct("a")])
        ds.rows["accounts"][0].data[EXTRA_KEY] = ["surplus"]
        out = validate_dataset(ds, parse_manifest(manifest(), CFG, now=NOW), CFG)
        self.assertEqual(reasons(out), ["malformed_row"])

    def test_output_is_sorted_for_stable_batching(self):
        out = run([acct("b"), acct("a"), acct("c")])
        self.assertEqual([a.platform_account_id for a in out.accounts], ["a", "b", "c"])


class RelationshipAndContentTests(unittest.TestCase):
    def test_direction_is_preserved_and_never_inferred(self):
        out = run(relationships=[edge("a", "b")])
        self.assertEqual([(e.source_account_id, e.target_account_id) for e in out.relationships], [("a", "b")])

    def test_relationship_faults(self):
        cases = {
            "self_relationship": edge("a", "a"),
            "invalid_enum:relationship_type": edge("a", "b", relationship_type="blocks"),
            "missing_required:relationship_type": edge("a", "b", relationship_type=""),
            "invalid_enum:verification_status": edge("a", "b", verification_status="trust_me"),
            "missing_required:target_account_id": edge("a", ""),
        }
        for expected, row in cases.items():
            with self.subTest(expected):
                self.assertIn(expected, reasons(run(relationships=[row])))

    def test_content_text_becomes_fingerprints_and_is_not_kept(self):
        text = "Huge giveaway today only claim your reward now"
        out = run(content=[post("c1", "a", "2026-09-30T09:00:00Z", text)])
        c = out.content[0]
        self.assertIsNotNone(c.content_hash)
        self.assertIsNotNone(c.simhash)
        self.assertEqual(c.text_length, len(text))
        self.assertFalse(hasattr(c, "text"))

    def test_quarantine_never_keeps_post_text(self):
        out = run(content=[post("c1", "a", "not-a-time", "secret words that should not be stored anywhere")])
        self.assertNotIn("secret words", json.dumps(out.quarantined[0].raw))


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.tmp = Path(self._t.name)

    def test_missing_required_column_rejects_the_file(self):
        d = self.tmp / "d"
        d.mkdir()
        (d / "manifest.json").write_text(json.dumps(manifest()))
        (d / "accounts.csv").write_text("platform,observed_at\nx,2026-01-01T00:00:00Z\n")
        with self.assertRaisesRegex(SchemaIncompatibleError, "missing required columns"):
            load_source(d, CFG)

    def test_unknown_columns_warn_but_do_not_fail(self):
        d = write_dir(self.tmp / "d", man=manifest(), accounts=[{**acct("a"), "favourite_colour": "teal"}])
        ds = load_source(d, CFG)
        self.assertTrue(any("favourite_colour" in w for w in ds.warnings))
        self.assertNotIn("favourite_colour", ds.rows["accounts"][0].data)

    def test_hash_depends_on_content(self):
        a = load_source(write_dir(self.tmp / "a", man=manifest(), accounts=[acct("a")]), CFG)
        b = load_source(write_dir(self.tmp / "b", man=manifest(), accounts=[acct("a")]), CFG)
        c = load_source(write_dir(self.tmp / "c", man=manifest(), accounts=[acct("a", follower_count=5)]), CFG)
        self.assertEqual(a.sha256, b.sha256)
        self.assertNotEqual(a.sha256, c.sha256)

    def test_json_bundle_and_csv_directory_agree(self):
        accounts = [acct("a"), acct("b")]
        rels = [edge("a", "b")]
        d = load_source(write_dir(self.tmp / "d", man=manifest(), accounts=accounts, relationships=rels), CFG)
        bundle = self.tmp / "b.json"
        bundle.write_text(json.dumps({"manifest": manifest(), "accounts": accounts, "relationships": rels}))
        b = load_source(bundle, CFG)
        m = parse_manifest(manifest(), CFG, now=NOW)
        vd, vb = validate_dataset(d, m, CFG), validate_dataset(b, m, CFG)
        self.assertEqual(vd.accounts, [type(a)(**{**a.__dict__, "source_ref": x.source_ref, "payload_sha256": x.payload_sha256})
                                       for a, x in zip(vb.accounts, vd.accounts, strict=True)])
        self.assertEqual([(e.source_account_id, e.target_account_id) for e in vd.relationships],
                         [(e.source_account_id, e.target_account_id) for e in vb.relationships])

    def test_bad_inputs_rejected(self):
        with self.assertRaises(SchemaIncompatibleError):
            load_source(self.tmp / "missing", CFG)
        nul = self.tmp / "n"
        nul.mkdir()
        (nul / "manifest.json").write_text(json.dumps(manifest()))
        (nul / "accounts.csv").write_bytes(b"platform,platform_account_id,observed_at\nx,a\x00b,2026-01-01T00:00:00Z\n")
        with self.assertRaisesRegex(SchemaIncompatibleError, "NUL"):
            load_source(nul, CFG)
        bad = self.tmp / "bad.json"
        bad.write_text("{not json")
        with self.assertRaises(SchemaIncompatibleError):
            load_source(bad, CFG)

    def test_size_and_row_limits_enforced(self):
        from dataclasses import replace
        d = write_dir(self.tmp / "d", man=manifest(), accounts=[acct(f"a{i}") for i in range(5)])
        with self.assertRaises(ImportLimitError):
            load_source(d, replace(CFG, max_records_per_file=3))
        with self.assertRaises(ImportLimitError):
            load_source(d, replace(CFG, max_file_bytes=10))


if __name__ == "__main__":
    unittest.main()
