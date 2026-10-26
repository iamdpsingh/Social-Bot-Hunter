import tempfile
import unittest
from pathlib import Path

from sbh.docgen import TABLE_DOCS, sync_docs
from sbh.features.definitions import CATALOGUE
from sbh.fixtures import synthetic
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations

REPO = Path(__file__).resolve().parents[2]


class GeneratedDocs(unittest.TestCase):
    def test_generated_tables_match_the_code(self):
        self.assertEqual(sync_docs(REPO / "docs", write=False), [],
                         "run: python -m sbh docs --write")

    def test_every_table_has_a_documented_purpose_grain_and_retention(self):
        db = SQLiteDatabase()
        apply_migrations(db)
        tables = {r["name"] for r in db.query_all("SELECT name FROM sqlite_master WHERE type='table'")} - {"schema_migrations"}
        self.assertEqual(tables, set(TABLE_DOCS))

    def test_every_feature_is_described_in_the_methodology(self):
        text = (REPO / "docs" / "detection-methodology.md").read_text()
        for name in CATALOGUE:
            if CATALOGUE[name] != "data_quality":
                self.assertIn(f"`{name}`", text, name)

    def test_required_documents_exist(self):
        for name in ("architecture", "platform-access-matrix", "data-dictionary", "detection-methodology", "model-card",
                     "privacy-and-retention", "testing-and-validation", "deployment", "monitoring-runbook", "status"):
            self.assertTrue((REPO / "docs" / f"{name}.md").is_file(), name)
        for name in ("README.md", "CONTRIBUTING.md", ".env.example"):
            self.assertTrue((REPO / name).is_file(), name)
        self.assertTrue(list((REPO / "docs" / "decisions").glob("*.md")))
        self.assertTrue(len(list((REPO / ".agents" / "rules").glob("*.md"))) >= 7)


class CommittedSample(unittest.TestCase):
    def test_committed_sample_is_exactly_what_the_generator_produces(self):
        with tempfile.TemporaryDirectory() as d:
            fresh = synthetic.write_csv_dir(synthetic.generate(42), Path(d) / "x")
            committed = REPO / "data" / "samples" / "synthetic_demo"
            for name in ("manifest.json", "accounts.csv", "relationships.csv", "content.csv"):
                self.assertEqual((fresh / name).read_bytes(), (committed / name).read_bytes(), name)

    def test_generator_is_deterministic_and_seed_sensitive(self):
        a, b, c = synthetic.generate(42), synthetic.generate(42), synthetic.generate(43)
        self.assertEqual(a.relationships, b.relationships)
        self.assertEqual(a.content, b.content)
        self.assertNotEqual(a.relationships, c.relationships)

    def test_sample_is_labelled_synthetic(self):
        m = synthetic.generate(42).manifest
        self.assertEqual(m["collection_method"], "synthetic")
        self.assertIn("SYNTHETIC", m["source_description"])


if __name__ == "__main__":
    unittest.main()
