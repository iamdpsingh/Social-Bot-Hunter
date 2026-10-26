import random
import unittest
from datetime import UTC, datetime

from sbh.config import load_config
from sbh.shared import jsonutil, timeutil
from sbh.shared.errors import ConfigError, PermanentError, TransientError
from sbh.shared.retry import retry_with_backoff
from sbh.shared.safety import clean_text, csv_safe_cell


class TimeTests(unittest.TestCase):
    def test_naive_timestamp_rejected(self):
        with self.assertRaisesRegex(ValueError, "no timezone"):
            timeutil.parse_timestamp("2026-01-01T00:00:00")

    def test_offsets_normalised_to_utc(self):
        dt = timeutil.parse_timestamp("2026-01-01T05:30:00+05:30")
        self.assertEqual(dt, datetime(2026, 1, 1, 0, 0, tzinfo=UTC))

    def test_implausibly_old_and_garbage_rejected(self):
        for bad in ("1999-12-31T00:00:00Z", "yesterday", "", None, 12345):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                timeutil.parse_timestamp(bad)

    def test_iso_is_fixed_width_so_text_order_is_time_order(self):
        a = timeutil.iso_utc(datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC))
        b = timeutil.iso_utc(datetime(2026, 1, 1, 0, 0, 0, 5, tzinfo=UTC))
        self.assertEqual(len(a), len(b))
        self.assertLess(a, b)

    def test_from_db_accepts_string_and_datetime(self):
        self.assertEqual(timeutil.from_db("2026-01-01T00:00:00.000000Z"), datetime(2026, 1, 1, tzinfo=UTC))
        self.assertEqual(timeutil.from_db(datetime(2026, 1, 1)), datetime(2026, 1, 1, tzinfo=UTC))
        self.assertIsNone(timeutil.from_db(None))


class ConfigTests(unittest.TestCase):
    def _raw(self):
        import copy
        return copy.deepcopy(load_config().raw)

    def test_default_loads_and_hash_is_stable(self):
        self.assertEqual(load_config().sha256, load_config().sha256)
        self.assertEqual(load_config().version, "rules-v1")

    def test_changing_a_weight_changes_the_hash(self):
        from sbh.config import _parse
        raw = self._raw()
        raw["scoring"]["rules"][0]["weight"] = 3.0
        self.assertNotEqual(_parse(raw).sha256, load_config().sha256)

    def test_invalid_configurations_rejected(self):
        from sbh.config import _parse
        cases = {
            "unknown key": lambda r: r["features"].update(typo=1),
            "missing key": lambda r: r["features"].pop("min_out_degree"),
            "duplicate rule": lambda r: r["scoring"]["rules"].append(dict(r["scoring"]["rules"][0])),
            "zero_at == full_at": lambda r: r["scoring"]["rules"][0].update(zero_at=1.0, full_at=1.0),
            "non-positive weight": lambda r: r["scoring"]["rules"][0].update(weight=0),
            "bands not from 0": lambda r: r["scoring"]["bands"].__setitem__(0, {"lower": 5, "label": "x"}),
            "coverage out of range": lambda r: r["scoring"].update(min_weight_coverage=1.5),
            "jaccard out of range": lambda r: r["graph"]["cluster"].update(jaccard_threshold=0),
            "float for int field": lambda r: r["imports"].update(batch_size=2.5),
        }
        for name, mutate in cases.items():
            raw = self._raw()
            mutate(raw)
            with self.subTest(name), self.assertRaises(ConfigError):
                _parse(raw)


class RetryTests(unittest.TestCase):
    def test_transient_then_success(self):
        calls, sleeps = [], []

        def fn():
            calls.append(1)
            if len(calls) < 3:
                raise TransientError("503")
            return "ok"

        self.assertEqual(retry_with_backoff(fn, sleep=sleeps.append, rng=random.Random(1)), "ok")
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(sleeps), 2)

    def test_permanent_error_never_retried(self):
        calls = []

        def fn():
            calls.append(1)
            raise PermanentError("403 forbidden")

        with self.assertRaises(PermanentError):
            retry_with_backoff(fn, sleep=lambda s: None)
        self.assertEqual(len(calls), 1)

    def test_attempts_are_bounded(self):
        calls = []

        def fn():
            calls.append(1)
            raise TransientError("timeout")

        with self.assertRaises(TransientError):
            retry_with_backoff(fn, max_attempts=4, sleep=lambda s: None)
        self.assertEqual(len(calls), 4)

    def test_backoff_is_capped_and_honours_retry_after(self):
        sleeps = []
        n = []

        def fn():
            n.append(1)
            if len(n) == 1:
                raise TransientError("429", retry_after=7.0)
            if len(n) < 8:
                raise TransientError("again")
            return 1

        retry_with_backoff(fn, max_attempts=10, base_delay=1.0, max_delay=10.0, sleep=sleeps.append,
                           rng=random.Random(3))
        self.assertGreaterEqual(sleeps[0], 7.0)
        self.assertTrue(all(s <= 10.0 for s in sleeps))


class SafetyTests(unittest.TestCase):
    def test_clean_text_strips_control_characters_and_refuses_to_truncate(self):
        self.assertEqual(clean_text("  ab\x00c\x07 ", 10), "abc")
        with self.assertRaises(ValueError):
            clean_text("x" * 11, 10)

    def test_csv_formula_injection_neutralised(self):
        for dangerous in ("=1+1", "+cmd", "-2", "@SUM(A1)", "\tx"):
            self.assertTrue(csv_safe_cell(dangerous).startswith("'"))
        self.assertEqual(csv_safe_cell("maya"), "maya")
        self.assertEqual(csv_safe_cell(None), "")

    def test_json_canonical_form_is_order_independent(self):
        self.assertEqual(jsonutil.dumps({"b": 1, "a": 2}), jsonutil.dumps({"a": 2, "b": 1}))
        self.assertEqual(jsonutil.loads('{"a":1}'), {"a": 1})
        self.assertEqual(jsonutil.loads({"a": 1}), {"a": 1})


if __name__ == "__main__":
    unittest.main()
