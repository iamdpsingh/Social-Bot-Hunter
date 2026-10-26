import unittest
from datetime import UTC, datetime, timedelta

from sbh.config import load_config
from sbh.detection.scoring import band_for, evidence_value, score_account
from sbh.features import account as F
from sbh.features.definitions import CATALOGUE, FeatureResult
from sbh.shared.models import Post
from sbh.storage.accounts import ObservationRow

CFG = load_config()
FC = CFG.features
REF = datetime(2026, 9, 30, 12, tzinfo=UTC)


def obs(i=0, hours_ago=1, **kw):
    base = dict(id=f"o{i}", platform_account_id="a", observed_at=REF - timedelta(hours=hours_ago), username="maya",
                display_name=None, follower_count=100, following_count=100, post_count=500, has_bio=True,
                bio_length=None, has_profile_image=True, has_display_name=True,
                account_created_at=REF - timedelta(days=400), is_verified=None, is_private=None)
    base.update(kw)
    return ObservationRow(**base)


def ctx(observations=(), posts=(), content_collected=True, **kw):
    return F.AccountContext("a", list(observations), list(posts), content_collected, **kw)


def posts_at(times, h=None):
    return [Post("a", t, h(i) if h else f"h{i}", None) for i, t in enumerate(times)]


class ProfileFeatures(unittest.TestCase):
    def test_ratio_uses_smoothing_so_zero_followers_is_defined(self):
        f = F.following_follower_ratio(ctx([obs(follower_count=0, following_count=99)]))
        self.assertEqual(f.value, 100.0)

    def test_missing_counts_are_unavailable_not_zero(self):
        f = F.following_follower_ratio(ctx([obs(follower_count=None)]))
        self.assertIsNone(f.value)
        self.assertIn("not observed", f.unavailable_reason)
        self.assertIsNone(F.following_follower_ratio(ctx([])).value)

    def test_zero_followers_is_a_real_value(self):
        self.assertIsNotNone(F.following_follower_ratio(ctx([obs(follower_count=0, following_count=0)])).value)

    def test_profile_completeness_uses_only_known_fields(self):
        f = F.profile_completeness(ctx([obs(has_bio=False, has_profile_image=True, has_display_name=None)]), FC)
        self.assertEqual(f.value, 0.5)
        thin = F.profile_completeness(ctx([obs(has_bio=None, has_profile_image=None, has_display_name=True)]), FC)
        self.assertIsNone(thin.value)

    def test_username_digit_ratio(self):
        self.assertEqual(F.username_digit_ratio(ctx([obs(username="user1234")])).value, 0.5)
        self.assertIsNone(F.username_digit_ratio(ctx([obs(username=None)])).value)

    def test_post_rate_needs_source_supplied_creation_time(self):
        self.assertIsNone(F.post_rate_per_day(ctx([obs(account_created_at=None)]), FC).value)  # never inferred
        young = F.post_rate_per_day(ctx([obs(account_created_at=REF - timedelta(days=2))]), FC)
        self.assertIsNone(young.value)
        self.assertIn("unstable", young.unavailable_reason)
        ok = F.post_rate_per_day(ctx([obs(post_count=4000, account_created_at=REF - timedelta(days=40, hours=1))]), FC)
        self.assertAlmostEqual(ok.value, 4000 / 40.0, delta=0.1)

    def test_growth_spike_needs_two_separated_observations(self):
        one = F.follower_growth_spike(ctx([obs()]), FC)
        self.assertIsNone(one.value)
        close = F.follower_growth_spike(ctx([obs(0, 1.5, follower_count=10), obs(1, 1.0, follower_count=900)]), FC)
        self.assertIsNone(close.value)  # 30 minutes apart is below the 1h minimum
        far = F.follower_growth_spike(ctx([obs(0, 300, follower_count=10), obs(1, 1, follower_count=260)]), FC)
        self.assertAlmostEqual(far.value, (260 - 10) / 50)  # denominator floored at 50
        shrink = F.follower_growth_spike(ctx([obs(0, 300, follower_count=900), obs(1, 1, follower_count=10)]), FC)
        self.assertEqual(shrink.value, 0.0)


class BehaviourFeatures(unittest.TestCase):
    def test_no_content_collected_is_unavailable_not_zero(self):
        self.assertIsNone(F.post_interval_cv(ctx(content_collected=False), FC).value)
        self.assertIsNone(F.duplicate_content_ratio(ctx(content_collected=False), FC).value)
        self.assertIsNone(F.posts_observed(ctx(content_collected=False)).value)
        self.assertEqual(F.posts_observed(ctx(content_collected=True)).value, 0.0)

    def test_interval_cv_regular_vs_irregular(self):
        regular = F.post_interval_cv(ctx(posts=posts_at([i * 3600.0 for i in range(10)])), FC)
        self.assertEqual(regular.value, 0.0)
        irregular = F.post_interval_cv(ctx(posts=posts_at([0, 10, 4000, 4100, 90000, 90500, 91000, 400000])), FC)
        self.assertGreater(irregular.value, 1.0)

    def test_interval_cv_needs_enough_posts(self):
        self.assertIsNone(F.post_interval_cv(ctx(posts=posts_at([0, 1, 2])), FC).value)

    def test_simultaneous_posts_are_treated_as_perfectly_regular(self):
        f = F.post_interval_cv(ctx(posts=posts_at([5.0] * 9)), FC)
        self.assertEqual(f.value, 0.0)
        self.assertTrue(f.details["all_posts_same_timestamp"])

    def test_duplicate_ratio(self):
        dup = [Post("a", float(i), "same" if i < 4 else f"u{i}", None) for i in range(8)]
        f = F.duplicate_content_ratio(ctx(posts=dup), FC)
        self.assertEqual(f.value, 4 / 8)
        distinct = F.duplicate_content_ratio(ctx(posts=posts_at(range(8))), FC)
        self.assertEqual(distinct.value, 0.0)
        self.assertIsNone(F.duplicate_content_ratio(ctx(posts=posts_at(range(3))), FC).value)


class NetworkFeatures(unittest.TestCase):
    def test_network_features_need_relationship_data_and_enough_follows(self):
        self.assertIsNone(F.max_following_jaccard(ctx(), FC).value)
        self.assertIsNone(F.max_following_jaccard(ctx(out_degree=3), FC).value)
        self.assertEqual(F.max_following_jaccard(ctx(out_degree=20, max_following_jaccard=None), FC).value, 0.0)
        self.assertEqual(F.max_following_jaccard(ctx(out_degree=20, max_following_jaccard=0.7), FC).value, 0.7)

    def test_reciprocity_only_over_checkable_follows(self):
        self.assertIsNone(F.reciprocity_ratio(ctx(out_degree=30, checkable_follows=2, mutual_count=0), FC).value)
        f = F.reciprocity_ratio(ctx(out_degree=30, checkable_follows=10, mutual_count=4), FC)
        self.assertEqual(f.value, 0.4)

    def test_data_quality_features(self):
        c = ctx([obs(follower_count=None, post_count=None)], list_completeness={"following": "complete"})
        self.assertAlmostEqual(F.field_availability(c).value, 6 / 8)
        self.assertEqual(F.relationship_coverage(c).value, 0.5)
        self.assertAlmostEqual(F.observation_age_days(c, REF).value, 1 / 24)
        self.assertEqual(F.observation_count(c).value, 1.0)
        self.assertIsNone(F.relationship_coverage(ctx([obs()])).value)

    def test_catalogue_covers_every_computed_feature(self):
        names = {f.name for f in F.compute_account_features(ctx([obs()]), FC, REF)}
        self.assertEqual(names, set(CATALOGUE))
        rule_features = {r.feature for r in CFG.scoring.rules}
        self.assertTrue(rule_features <= set(CATALOGUE))
        self.assertTrue(all(CATALOGUE[n] != "data_quality" for n in rule_features))


class Scoring(unittest.TestCase):
    rules = {r.feature: r for r in CFG.scoring.rules}

    def feats(self, **values):
        return {k: FeatureResult.ok(k, v) for k, v in values.items()}

    def test_ramp_both_directions_and_clamping(self):
        up = self.rules["following_follower_ratio"]          # 5 -> 0, 50 -> 1
        self.assertEqual(evidence_value(up, 5), 0.0)
        self.assertEqual(evidence_value(up, 50), 1.0)
        self.assertEqual(evidence_value(up, 1000), 1.0)
        self.assertAlmostEqual(evidence_value(up, 27.5), 0.5)
        down = self.rules["profile_completeness"]            # 1.0 -> 0, 0.0 -> 1
        self.assertEqual(evidence_value(down, 1.0), 0.0)
        self.assertEqual(evidence_value(down, 0.0), 1.0)
        self.assertEqual(evidence_value(down, -3), 1.0)

    def test_bands(self):
        b = CFG.scoring.bands
        self.assertEqual(band_for(0, b), "lower_observed_risk")
        self.assertEqual(band_for(24.99, b), "lower_observed_risk")
        self.assertEqual(band_for(25, b), "some_suspicious_indicators")
        self.assertEqual(band_for(50, b), "elevated_risk_indicators")
        self.assertEqual(band_for(75, b), "strong_combination_of_indicators")
        self.assertEqual(band_for(100, b), "strong_combination_of_indicators")

    def test_score_formula_matches_hand_calculation(self):
        f = self.feats(following_follower_ratio=50.0, profile_completeness=1.0, username_digit_ratio=0.8,
                       post_rate_per_day=30.0)
        res = score_account(f, CFG.scoring)
        # w: ratio 1.0*e1.0, profile 0.75*e0, username 0.5*e1.0, post_rate 1.0*e0 ; sum(w)=3.25
        self.assertEqual(res.status, "insufficient_evidence")  # weight coverage 3.25/9.75 = 33% < 40%
        f2 = {**f, **self.feats(duplicate_content_ratio=0.8)}
        res2 = score_account(f2, CFG.scoring)
        self.assertEqual(res2.status, "scored")
        self.assertAlmostEqual(res2.score, 100 * (1.0 + 0.5 + 2.0) / (3.25 + 2.0), places=2)

    def test_contribution_points_sum_to_the_score(self):
        f = self.feats(following_follower_ratio=20.0, profile_completeness=0.3, username_digit_ratio=0.6,
                       post_rate_per_day=100.0, duplicate_content_ratio=0.5, max_following_jaccard=0.6)
        res = score_account(f, CFG.scoring)
        pts = sum(c["points"] for c in res.contributions if c["available"])
        self.assertAlmostEqual(pts, res.score, delta=0.01)

    def test_unavailable_features_lower_coverage_but_are_not_scored_as_zero(self):
        full = self.feats(following_follower_ratio=50.0, profile_completeness=0.0, username_digit_ratio=0.8,
                          post_rate_per_day=150.0, post_interval_cv=0.1, duplicate_content_ratio=0.8,
                          follower_growth_spike=5.0, max_following_jaccard=0.8, reciprocity_ratio=0.05)
        self.assertEqual(score_account(full, CFG.scoring).score, 100.0)
        partial = {k: v for k, v in full.items() if k not in ("follower_growth_spike", "reciprocity_ratio")}
        res = score_account(partial, CFG.scoring)
        self.assertEqual(res.score, 100.0)  # missing evidence neither raises nor lowers the score
        self.assertAlmostEqual(res.evidence_coverage, (9.75 - 1.0) / 9.75, places=3)
        self.assertTrue(any("follower_growth_spike unavailable" in x for x in res.limitations))

    def test_insufficient_evidence_returns_no_score_and_says_why(self):
        res = score_account(self.feats(following_follower_ratio=99.0), CFG.scoring)
        self.assertEqual((res.status, res.score, res.band), ("insufficient_evidence", None, None))
        self.assertTrue(any("Insufficient evidence" in x for x in res.limitations))

    def test_every_result_carries_the_not_proof_disclaimer(self):
        res = score_account({}, CFG.scoring)
        self.assertIn("not proof", res.limitations[0])


if __name__ == "__main__":
    unittest.main()
