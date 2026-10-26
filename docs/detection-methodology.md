# Detection methodology

Version `rules-v1` (configuration), `features-v1` (feature definitions), graph method
`similarity-louvain` version 1.

**What this produces:** heuristic *risk indicators* and *candidate* coordinated groups, each with the
evidence behind it, the data coverage it rests on, and the explanations that remain possible. **What
it does not produce:** proof that an account is a bot, a verified fake-follower percentage, or any
statement about intent. A high score means "a strong combination of suspicious indicators was
observed", nothing more.

All thresholds and weights live in `src/sbh/resources/detection.v1.yaml`. They are initial heuristics
chosen for interpretability and have **not** been tuned or validated against labelled real data
(see `model-card.md`).

## 1. Observed facts vs. computed vs. judged

| Layer | Example | Where stored |
|---|---|---|
| Observed fact | `following_count = 1900` in an observation | `account_observations` |
| Computed feature | `following_follower_ratio = 63.3` | `account_features` |
| Heuristic indicator | risk score 79.0, band `strong_combination_of_indicators` | `risk_assessments` |
| Candidate cluster | 10 accounts, signal strength `high`, confidence `moderate` | `network_clusters` |
| Human conclusion | `review_status` (starts `unreviewed`) | `network_clusters` |
| Unknown | feature unavailable with a reason | `account_features` |

## 2. Account features (`features-v1`)

Only features the source data supports are calculated. A feature that cannot be calculated is
*unavailable* with a stated reason, and is never treated as zero.

| Feature | Definition | Unavailable when |
|---|---|---|
| `following_follower_ratio` | (following + 1) / (followers + 1) | either count not observed |
| `profile_completeness` | present / known among bio, profile image, display name | fewer than 2 of the 3 fields known |
| `username_digit_ratio` | digits / username length | username not observed |
| `post_rate_per_day` | post_count / account age, age from the **source-supplied** creation time | no creation time, no post count, or account younger than 7 days |
| `post_interval_cv` | std / mean of gaps between observed posts | no content in the scan, or fewer than 8 posts |
| `duplicate_content_ratio` | share of posts that exactly or near-duplicate another post by the same account | no content, or fewer than 5 fingerprinted posts |
| `follower_growth_spike` | largest relative follower increase between consecutive observations at least 1h apart (denominator floored at 50) | fewer than two such observations |
| `max_following_jaccard` | highest Jaccard overlap of followed accounts with any other observed account | no relationship data, or fewer than 10 observed follows |
| `reciprocity_ratio` | mutual follows / follows whose own following list is complete | fewer than 5 such "checkable" follows |
| data-quality features | `observation_age_days`, `field_availability`, `observation_count`, `relationship_coverage`, `posts_observed` | carry no scoring weight; shown next to every score |

Things the system deliberately does **not** do: infer a creation date from a username or from the
first observation date; treat verification status, profile photos, posting frequency or follower
counts as proof of automation; link accounts across platforms by username.

`reciprocity_ratio` needs a note. "A follows B but B does not follow A" is only meaningful if B's
following list was actually collected. Otherwise "no edge back" just means "not observed", and
almost every account would look unreciprocated. So reciprocity counts only follows whose own
following list is declared complete.

## 3. Risk score

```
R = 100 * sum(w_i * e_i) / sum(w_i)        over rules whose feature is available
e_i = clamp((value - zero_at) / (full_at - zero_at), 0, 1)
```

The same ramp formula covers "high is suspicious" (`zero_at < full_at`) and "low is suspicious"
(`zero_at > full_at`).

<!-- BEGIN GENERATED:scoring-rules -->
| Feature | Weight | Share | Evidence 0 at | Evidence 1 at | What it measures |
|---|---|---|---|---|---|
| `following_follower_ratio` | 1 | 10.3% | 5 | 50 | Accounts that follow far more accounts than follow them back. Common among new legitimate users too. |
| `profile_completeness` | 0.75 | 7.7% | 1 | 0 | Share of observed profile fields (bio, image, display name) that are present. |
| `username_digit_ratio` | 0.5 | 5.1% | 0.4 | 0.8 | Fraction of username characters that are digits (auto-generated handles). |
| `post_rate_per_day` | 1 | 10.3% | 30 | 150 | Lifetime posts per day, from source-supplied account creation time. |
| `post_interval_cv` | 1.5 | 15.4% | 0.6 | 0.1 | Coefficient of variation of gaps between posts. Very regular posting is machine-like. |
| `duplicate_content_ratio` | 2 | 20.5% | 0.2 | 0.8 | Share of an account's posts that duplicate or near-duplicate another of its posts. |
| `follower_growth_spike` | 0.5 | 5.1% | 1 | 5 | Largest relative follower increase between consecutive observations. Viral growth is legitimate. |
| `max_following_jaccard` | 2 | 20.5% | 0.3 | 0.8 | Highest overlap of followed accounts with any other observed account. Friend groups also score high. |
| `reciprocity_ratio` | 0.5 | 5.1% | 0.3 | 0.05 | Share of followed accounts that follow back. Low reciprocity with many follows is weakly suspicious. |

Configuration version `rules-v1`; minimum 3 available rules and 40% weight coverage, otherwise the result is `insufficient_evidence`.

| Band (score at least) | Label |
|---|---|
| 0 | `lower_observed_risk` |
| 25 | `some_suspicious_indicators` |
| 50 | `elevated_risk_indicators` |
| 75 | `strong_combination_of_indicators` |
<!-- END GENERATED:scoring-rules -->

* Unavailable rules are removed from both sums. They reduce `evidence_coverage` (available weight /
  total weight), but they do not lower or raise the score.
* **Minimum evidence:** at least `min_features` rules and `min_weight_coverage` of the weight must be
  available. Otherwise the result is `insufficient_evidence` and *no score is produced*.
* Each rule's contribution in score points is stored, and the points add up to the score exactly.
  Every contribution with positive evidence also gets an `evidence_records` row with a source
  reference, so a score can always be traced back to rows.
* The bands are display labels for heuristic risk, not probabilities.

## 4. Coordinated-network detection

Graph: directed, one graph per platform and per scan. `(a, b)` means *a follows b*. Identity
namespaces never merge across platforms.

Signals computed:

| Signal | Implementation |
|---|---|
| Neighbourhood Jaccard similarity | Followed-account sets, with the pair's own two members excluded from each other's sets. Candidate pairs come from an inverted index, not all N² pairs. Followers-side similarity (`direction='in'`) is implemented but not used for clustering in v1. |
| Shared follow targets | Accounts outside the group followed by at least 60% of members |
| Mutual connection patterns | Fraction of member pairs that follow each other |
| Community detection | Seeded Louvain on the whole follow graph, for context (how many communities the members span) |
| Degree distributions, density, reciprocity | `graph_summary`, stored on the scan |
| Dense subgraphs | Internal follow density and the share of members' follows that stay inside the group |
| Repeated content | Cross-member exact/near duplicates (see below) |
| Temporal synchronisation | Observed vs. expected cross-member co-posting within ±60s |
| Structure across scans | `diff_edge_sets`, which respects list coverage (section 6) |

**Cluster formation (`similarity-louvain` v1).** Keep account pairs with Jaccard >= 0.5, at least 5
shared targets, and at least 10 observed follows each. Group them with seeded Louvain on that
similarity graph. Keep groups of 3 to 500 accounts.

**Evidence and strength.** For each group the detector looks for three *independent behavioural*
signals: repeated content across members, timing synchronisation, and elevated member risk scores.

| Behavioural signals present | `signal_strength` |
|---|---|
| 0 (structure only) | `low` |
| 1 | `moderate` |
| 2 or more | `high` |

Structural similarity alone is never more than `low`, because friend groups, fandoms, teams and
professional communities overlap heavily too. **Confidence** is `moderate` only when at least 80% of
members have a profile observation and at least 80% have a complete following list; otherwise `low`.
The detector never sets `high` confidence.

**Alternative explanations** are generated from the metrics and stored with every cluster: shared
interests, high mutual-follow rate (friend group), shared targets that are popular accounts
(popularity is measured *excluding* the members' own follows, otherwise the group inflates its own
targets), absence of any behavioural evidence, and incomplete data.

### Near-duplicate content

Only fingerprints are stored. The exact hash is SHA-256 of case/whitespace-normalised text. The
near-duplicate fingerprint is a 64-bit SimHash over 3-word shingles, computed after replacing URLs
and @mentions with placeholders, and posts count as near-duplicates at Hamming distance <= 6.

This is deliberately conservative. It catches repeated templates with rotating links or handles and
tiny edits to long posts. A one-word substitution in a short post lands about 15 bits away, so
"spinner" bots that swap words evade it. Posts shorter than 5 words get no SimHash (exact hash only).

### Temporal synchronisation

For each pair of members: posts of one that have a post of the other within ±w seconds, compared
with the expectation if both posted at uniformly random times over the common span. `lift =
observed / expected`; the signal needs lift >= 3 and at least 5 observed co-posts.

Limitation: real people do not post uniformly (they sleep), so organic groups can show lift above 1.
The threshold of 3 sits well above that, but a modest lift is weak evidence and every cluster says so.

## 5. Limits and failure behaviour

Graph building and similarity enforce configurable node, edge, candidate-pair and runtime limits.
Exceeding a limit **never truncates silently**: the stage records the reason, the scan becomes
`partial`, network features are unavailable, no clusters are produced, and the rest of the data is
kept. Celebrity-scale targets (followed by more than 300 accounts in the scan) are skipped during
candidate-pair generation, are counted in the scan's `similarity.skipped_hub_targets`, and still count
in the exact Jaccard.

## 6. Comparing scans

Different scans can observe different amounts of the network, so "an edge disappeared" is not
automatically "someone unfollowed". `diff_edge_sets` classifies each difference:

| Class | Meaning |
|---|---|
| `confirmed_removed` | Absent now, and a **complete** list that would contain the edge was collected in the later scan |
| `not_reobserved` | Absent now, but no complete list covers it: may be incomplete collection |
| `confirmed_added` | Present now, and a complete list in the earlier scan proves it was absent |
| `newly_observed` | Present now, but the earlier collection was incomplete: may not be new |
| `unchanged` | In both |

## 7. Known limitations

* No labelled real-world data was used. Weights and thresholds are not calibrated.
* Account-level indicators are partly confounded by legitimate behaviour (new users, brand accounts,
  very active people). The `max_following_jaccard` rule scores friend groups too.
* Timing evidence assumes uniform posting as its baseline.
* Near-duplicate detection is conservative (above).
* Everything depends on the quality and declared coverage of the imported data.
