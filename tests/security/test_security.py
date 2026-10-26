import re
import unittest
from pathlib import Path

from sbh.config import load_config
from sbh.fixtures import synthetic
from sbh.pipeline.run import import_dataset
from sbh.shared.safety import csv_safe_cell
from tests.support import DbTestCase, acct, edge, manifest, post, synthetic_dir, write_dir

CFG = load_config()
REPO = Path(__file__).resolve().parents[2]


def dump_all_text(db) -> str:
    """Every value of every table as one string (SQLite introspection; test-only)."""
    chunks = []
    for t in db.query_all("SELECT name FROM sqlite_master WHERE type = 'table'"):
        for row in db.query_all(f"SELECT * FROM {t['name']}"):
            chunks.append(" ".join(str(v) for v in row.values() if v is not None))
    return "\n".join(chunks)


class DataMinimisation(DbTestCase):
    def test_raw_post_text_is_never_stored_only_fingerprints(self):
        import_dataset(self.db, synthetic_dir(), CFG)
        everything = dump_all_text(self.db).casefold()
        for fragment in ("giveaway", "premium followers", "crypto opportunity", "bit.ly", "free phone"):
            self.assertNotIn(fragment, everything)
        organic_words = synthetic.generate(42).content[0]["text"].casefold()
        self.assertNotIn(organic_words, everything)
        row = self.db.query_one("SELECT content_hash, simhash, text_length FROM content_observations LIMIT 1")
        self.assertTrue(row["content_hash"] and row["text_length"])

    def test_columns_of_content_table_have_no_text_field(self):
        cols = {r["name"] for r in self.db.query_all("PRAGMA table_info(content_observations)")}
        self.assertFalse({"text", "body", "content", "raw"} & cols)

    def test_quarantine_keeps_no_post_text(self):
        d = write_dir(self.tmp / "d", man=manifest(), accounts=[acct("a"), acct("b")] + [acct(f"x{i}") for i in range(20)],
                      content=[post("c1", "a", "not-a-time", "my very private words in a rejected post")])
        import_dataset(self.db, d, CFG)
        self.assertNotIn("private words", dump_all_text(self.db))


class HostileInput(DbTestCase):
    def test_sql_injection_strings_are_data_not_code(self):
        evil = "x'; DROP TABLE platform_accounts; --"
        d = write_dir(self.tmp / "d", man=manifest(), accounts=[acct("a", username=evil, display_name='"; DELETE FROM scan_jobs; --')],
                      relationships=[edge("a", "b")])
        import_dataset(self.db, d, CFG)
        self.assertEqual(self.db.query_one("SELECT username FROM platform_accounts WHERE platform_account_id = 'a'")["username"], evil)
        self.assertEqual(self.count("scan_jobs"), 1)

    def test_identifiers_cannot_carry_markup_paths_or_sql(self):
        for bad in ("../../etc/passwd", "<script>alert(1)</script>", "a b", "a;b", "a'b", "a/b"):
            d = write_dir(self.tmp / ("d" + str(abs(hash(bad)))), man=manifest(),
                          accounts=[acct(bad)] + [acct(f"ok{i}") for i in range(30)])
            res = import_dataset(self.db, d, CFG)
            self.assertEqual(self.count("platform_accounts", "platform_account_id = :b", b=bad), 0, bad)
            self.assertTrue(res.summary["quarantined_records"] >= 1)

    def test_oversized_and_control_character_fields_are_rejected_or_cleaned(self):
        rows = [acct("long", username="u" * 500), acct("ctl", username="ma\x07ya\x1b"), acct("long2", display_name="d" * 999)]
        rows += [acct(f"ok{i}") for i in range(30)]
        import_dataset(self.db, write_dir(self.tmp / "d", man=manifest(), accounts=rows), CFG)
        self.assertEqual(self.count("platform_accounts", "platform_account_id IN ('long', 'long2')"), 0)
        cleaned = self.db.query_one("SELECT o.username AS username FROM account_observations o JOIN platform_accounts a "
                                    "ON a.id = o.platform_account_id WHERE a.platform_account_id = 'ctl'")
        self.assertEqual(cleaned["username"], "maya")

    def test_wrongly_typed_json_values_do_not_crash_the_importer(self):
        import json
        bundle = self.tmp / "b.json"
        bundle.write_text(json.dumps({"manifest": manifest(), "accounts": [
            {"platform": "x", "platform_account_id": "a", "observed_at": "2026-09-30T10:00:00Z", "follower_count": [1, 2]},
            {"platform": "x", "platform_account_id": {"nested": 1}, "observed_at": "2026-09-30T10:00:00Z"},
            "just a string", None,
            *[{"platform": "x", "platform_account_id": f"ok{i}", "observed_at": "2026-09-30T10:00:00Z"} for i in range(40)]]}))
        res = import_dataset(self.db, bundle, CFG)
        self.assertEqual(self.count("quarantined_records", "kind = 'invalid'"), 4)
        self.assertEqual(res.summary["accounts_with_profile_observation"], 40)

    def test_formula_usernames_are_stored_verbatim_but_neutralised_on_export(self):
        d = write_dir(self.tmp / "d", man=manifest(), accounts=[acct("a", username="=HYPERLINK(1)")] + [acct(f"ok{i}") for i in range(30)])
        import_dataset(self.db, d, CFG)
        stored = self.db.query_one("SELECT username FROM platform_accounts WHERE platform_account_id = 'a'")["username"]
        self.assertEqual(stored, "=HYPERLINK(1)")
        self.assertTrue(csv_safe_cell(stored).startswith("'"))


class LogHygiene(DbTestCase):
    def test_logs_contain_counts_and_scan_ids_but_no_content_or_usernames(self):
        with self.assertLogs("sbh", level="INFO") as captured:
            import_dataset(self.db, synthetic_dir(), CFG)
        text = " ".join(r.getMessage() + str(r.__dict__) for r in captured.records).casefold()
        self.assertTrue(captured.records)
        for needle in ("giveaway", "bit.ly", "password", "token", "secret"):
            self.assertNotIn(needle, text)
        usernames = {a["username"].casefold() for a in synthetic.generate(42).accounts if a["username"]}
        self.assertFalse([u for u in usernames if u in text])


class Secrets(unittest.TestCase):
    PATTERNS = {
        "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
        "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
        "Google API key": re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
        "Anthropic/OpenAI style key": re.compile(r"\bsk-[A-Za-z0-9_\-]{30,}"),
    }

    def test_no_credential_shaped_strings_in_the_repository(self):
        offenders = []
        for p in REPO.rglob("*"):
            if not p.is_file() or any(part in {".git", "__pycache__", "node_modules"} for part in p.parts):
                continue
            if p.suffix in {".pyc", ".sqlite", ".zip", ".png"} or p.name == "test_security.py":
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for label, rx in self.PATTERNS.items():
                if rx.search(text):
                    offenders.append(f"{p.relative_to(REPO)}: {label}")
        self.assertEqual(offenders, [])

    def test_env_files_are_gitignored_and_example_has_only_placeholders(self):
        self.assertIn(".env", (REPO / ".gitignore").read_text().splitlines())
        example = (REPO / ".env.example").read_text()
        self.assertIn("CHANGE_ME", example)
        self.assertNotRegex(example, r"(?m)^[A-Z_]*(SECRET|TOKEN|API_KEY)[A-Z_]*=\S+")


if __name__ == "__main__":
    unittest.main()
