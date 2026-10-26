"""End-to-end dataset scan: validate -> persist -> features -> scores -> clusters.

Reliability properties:
* **Idempotent.** The input's SHA-256 is unique; importing the same bytes again is a no-op.
  Row inserts use ``ON CONFLICT DO NOTHING``; derived outputs are replaced per (scan, version).
* **Restartable.** Every write batch commits together with its checkpoint, so a crash leaves the
  database consistent and a re-run continues from the last committed batch.
* **Honest outcomes.** A scan is ``complete`` only if nothing was rejected, nothing was skipped,
  and every relationship list is declared complete. Otherwise it is ``partial`` with the reasons
  recorded. Pipeline failures are never reported as findings about accounts.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

import networkx as nx

from sbh.config import Config
from sbh.contracts.capabilities import CapabilityRegistry, Operation, default_registry
from sbh.contracts.platforms import Platform
from sbh.detection.scoring import evidence_summary, score_account
from sbh.features.account import AccountContext, compute_account_features
from sbh.features.definitions import CATALOGUE, FEATURE_VERSION, FeatureResult
from sbh.graph.build import Deadline, build_graph
from sbh.graph.clusters import METHOD, METHOD_VERSION, detect_clusters
from sbh.graph.community import detect_communities, node_community_index
from sbh.graph.metrics import NodeNetworkMetrics, graph_summary, node_metrics
from sbh.graph.similarity import SimilarPair, neighbour_pairs
from sbh.schemas.io import RawDataset, load_source
from sbh.schemas.records import Completeness, ListKind
from sbh.schemas.validation import ValidationOutcome, parse_manifest, validate_dataset
from sbh.shared import jsonutil
from sbh.shared.errors import (
    GraphLimitExceeded,
    InvalidTransitionError,
    SbhError,
    ScanFailedError,
    ScanInProgressError,
    SchemaIncompatibleError,
)
from sbh.shared.logging import scan_context
from sbh.shared.models import Post
from sbh.shared.timeutil import utcnow
from sbh.storage.accounts import AccountRepository, AccountSeen
from sbh.storage.analysis import (
    AnalysisRepository,
    AssessmentRow,
    ClusterRow,
    EvidenceRow,
    FeatureRow,
)
from sbh.storage.content import ContentRepository
from sbh.storage.database import Database
from sbh.storage.edges import CoverageRow, EdgeRepository
from sbh.storage.scans import ScanRepository

log = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass
class ScanResult:
    scan_id: str
    status: str
    already_imported: bool = False
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class _GraphState:
    graph: nx.DiGraph
    pairs: list[SimilarPair]
    pair_stats: dict[str, Any]
    metrics: dict[str, NodeNetworkMetrics]


class DatasetScanRunner:
    def __init__(self, db: Database, cfg: Config, *, requested_by: str = "system",
                 registry: CapabilityRegistry | None = None,
                 clock: Callable[[], datetime] = utcnow) -> None:
        self.db, self.cfg, self.clock = db, cfg, clock
        self.requested_by = requested_by
        self.registry = registry or default_registry()
        self.scans = ScanRepository(db, clock)
        self.accounts = AccountRepository(db, clock)
        self.edges = EdgeRepository(db, clock)
        self.content = ContentRepository(db, clock)
        self.analysis = AnalysisRepository(db, clock)
        self._graph_state: _GraphState | None = None
        self._graph_error: str | None = None

    # ------------------------------------------------------------------ entry point
    def run(self, source: str | Path, *, allow_resume_running: bool = False) -> ScanResult:
        cfg = self.cfg
        try:
            raw = load_source(source, cfg.imports)
            manifest = parse_manifest(raw.manifest, cfg.imports, now=self.clock())
        except SchemaIncompatibleError as exc:
            self.scans.audit(self.requested_by, "import_rejected", "dataset", None,
                             {"source": str(Path(str(source)).name), "reason": str(exc)[:500]})
            raise

        ok, why = self.registry.can_collect(Platform(manifest.platform), Operation.DATASET_IMPORT)
        if not ok:
            raise SbhError(why)

        existing = self.scans.find_dataset_import(raw.sha256)
        if existing:
            scan_id = existing["scan_id"]
            scan = self.scans.get_scan(scan_id)
            assert scan is not None
            if scan["status"] in ("complete", "partial"):
                log.info("input already imported; nothing to do", extra={"scan": scan_id})
                return ScanResult(scan_id, scan["status"], already_imported=True,
                                  summary=scan["status_detail"].get("summary", {}))
            if scan["status"] == "running" and not allow_resume_running:
                raise ScanInProgressError(
                    f"scan {scan_id} for this input is marked running; if no worker is alive, "
                    "re-run with allow_resume_running=True")
            if scan["status"] == "cancelled":
                raise InvalidTransitionError(f"scan {scan_id} was cancelled and cannot be resumed")
            from_states = {"failed": ["failed"], "pending": ["pending"], "running": []}.get(scan["status"], [])
            self.scans.audit(self.requested_by, "scan_resumed", "scan", scan_id, {"from": scan["status"]})
            if scan["status"] == "failed":
                self.scans.merge_detail(scan_id, {"failure_history": [
                    *scan["status_detail"].get("failure_history", []), scan["failure_reason"]]})
            if from_states:
                self.scans.transition(scan_id, "running", from_states)
        else:
            with self.db.transaction():
                scan_id = self.scans.create_scan(
                    scan_type="dataset_import", collection_mode="dataset_import",
                    platform=manifest.platform,
                    data_origin="synthetic" if manifest.is_synthetic else "imported",
                    requested_by=self.requested_by, reference_time=manifest.collected_at,
                    config_version=cfg.version, config_sha256=cfg.sha256)
                self.scans.create_dataset_import(
                    scan_id=scan_id, dataset_name=manifest.dataset_name, source_name=raw.source_name,
                    sha256=raw.sha256, schema_version=manifest.schema_version,
                    collection_method=manifest.collection_method.value,
                    source_description=manifest.source_description, is_synthetic=manifest.is_synthetic,
                    manifest=raw.manifest)
                self.scans.audit(self.requested_by, "scan_created", "scan", scan_id,
                                 {"dataset": manifest.dataset_name, "sha256": raw.sha256})
                self.scans.transition(scan_id, "running", ["pending"])

        with scan_context(scan_id):
            try:
                return self._execute(scan_id, raw, manifest)
            except Exception as exc:
                reason = f"{type(exc).__name__}: {exc}"[:500]
                log.error("scan failed", extra={"reason": reason})
                try:
                    self.scans.transition(scan_id, "failed", ["running"], failure_reason=reason)
                    self.scans.audit(self.requested_by, "scan_failed", "scan", scan_id, {"reason": reason})
                except InvalidTransitionError:  # already in a terminal state; keep the original error
                    pass
                raise ScanFailedError(scan_id, reason) from exc

    # ------------------------------------------------------------------ stages
    def _execute(self, scan_id: str, raw: RawDataset, manifest: Any) -> ScanResult:
        cfg, db = self.cfg, self.db
        ref = manifest.collected_at
        prov = f"dataset_import:{manifest.dataset_name}:{raw.sha256[:12]}"

        # 1. validate (deterministic, so it is simply recomputed after a restart)
        outcome = validate_dataset(raw, manifest, cfg.imports)
        with db.transaction():
            self.scans.add_quarantine(scan_id, outcome.quarantined)
        total_rows = sum(len(v) for v in raw.rows.values())
        invalid = outcome.rejected_count
        if total_rows and invalid / total_rows > cfg.imports.max_invalid_fraction:
            raise ValueError(
                f"too_many_invalid_records: {invalid} of {total_rows} rows rejected "
                f"(limit {cfg.imports.max_invalid_fraction:.0%})")
        warnings = list(outcome.warnings)
        prev = self.scans.previous_import(manifest.dataset_name, manifest.platform, scan_id)
        if prev:
            for entity, n in outcome.stats["accepted"].items():
                before = (prev["record_counts"].get("accepted") or {}).get(entity, 0)
                if before and abs(n - before) / before > cfg.imports.row_count_change_warn_ratio:
                    warnings.append(f"{entity} row count changed from {before} to {n} since the previous "
                                    f"import of '{manifest.dataset_name}'")
        self.scans.merge_detail(scan_id, {"data_quality_warnings": warnings,
                                          "validation": outcome.stats})
        self.scans.set_record_counts(scan_id, outcome.stats)
        log.info("validated", extra=outcome.stats["accepted"])

        # 2. persist (batched, checkpointed)
        self._persist(scan_id, manifest.platform, ref, prov, outcome)
        completeness = self._persist_coverage(scan_id, manifest, outcome)

        # 3-5. analysis
        self._features_stage(scan_id, ref, outcome)
        self._detection_stage(scan_id)
        self._cluster_stage(scan_id, ref, outcome)

        # 6. outcome
        reasons: list[str] = []
        if invalid:
            reasons.append(f"{invalid} record(s) rejected during validation (see quarantined_records)")
        if completeness != "complete":
            reasons.append(f"relationship collection completeness is '{completeness}'")
        if self._graph_error:
            reasons.append(f"graph analysis skipped: {self._graph_error}")
        status = "partial" if reasons else "complete"
        summary = self._summary(scan_id)
        self.scans.merge_detail(scan_id, {"summary": summary, "partial_reasons": reasons})
        self.scans.transition(scan_id, status, ["running"], completeness=completeness)
        self.scans.audit(self.requested_by, "scan_finished", "scan", scan_id,
                         {"status": status, "reasons": reasons})
        log.info("scan finished", extra={"status": status})
        return ScanResult(scan_id, status, summary=summary)

    def _batched(self, scan_id: str, stage: str, items: Sequence[T], write: Callable[[Sequence[T]], None]) -> None:
        cp = self.scans.get_checkpoint(scan_id, stage)
        if cp and cp[1]:
            return
        start = cp[0] if cp else 0
        size = self.cfg.imports.batch_size
        if not items:
            self.scans.set_checkpoint(scan_id, stage, 0, True)
            return
        for i in range(start, len(items), size):
            chunk = items[i : i + size]
            with self.db.transaction():  # the batch and its checkpoint commit (or roll back) together
                write(chunk)
                end = i + len(chunk)
                self.scans.set_checkpoint(scan_id, stage, end, end >= len(items))

    def _persist(self, scan_id: str, platform: str, ref: datetime, prov: str, out: ValidationOutcome) -> None:
        # Accounts: one upsert item per observation, plus a stub for every endpoint/author with none.
        first_seen: dict[str, datetime] = {}
        for e in out.relationships:
            for pid in (e.source_account_id, e.target_account_id):
                first_seen[pid] = min(first_seen.get(pid, e.observed_at), e.observed_at)
        for c in out.content:
            first_seen[c.author_account_id] = min(first_seen.get(c.author_account_id, c.published_at),
                                                  c.published_at)
        observed_ids = {a.platform_account_id for a in out.accounts}
        items = [AccountSeen(a.platform_account_id, a.observed_at, a.username, a.display_name)
                 for a in out.accounts]
        items += [AccountSeen(pid, ts) for pid, ts in sorted(first_seen.items()) if pid not in observed_ids]
        self._batched(scan_id, "persist_accounts", items,
                      lambda chunk: self.accounts.ensure_accounts(scan_id, platform, prov, chunk))

        def ids_for(pids: set[str]) -> dict[str, str]:
            return self.accounts.resolve_ids(platform, sorted(pids))

        self._batched(scan_id, "persist_observations", out.accounts, lambda ch: self.accounts.insert_observations(
            scan_id, ref, prov, ch, ids_for({r.platform_account_id for r in ch})))
        self._batched(scan_id, "persist_relationships", out.relationships, lambda ch: self.edges.insert_edges(
            scan_id, ref, prov, ch,
            ids_for({r.source_account_id for r in ch} | {r.target_account_id for r in ch})))
        self._batched(scan_id, "persist_content", out.content, lambda ch: self.content.insert_content(
            scan_id, ref, prov, ch, ids_for({r.author_account_id for r in ch})))

    def _persist_coverage(self, scan_id: str, manifest: Any, out: ValidationOutcome) -> str:
        following: dict[str, int] = {}
        followers: dict[str, int] = {}
        for e in out.relationships:
            following[e.source_account_id] = following.get(e.source_account_id, 0) + 1
            followers[e.target_account_id] = followers.get(e.target_account_id, 0) + 1
        keys: dict[tuple[str, str], int] = {(a, ListKind.FOLLOWING.value): n for a, n in following.items()}
        keys.update({(a, ListKind.FOLLOWERS.value): n for a, n in followers.items()})
        for (acct, kind) in out.coverage_overrides:
            keys.setdefault((acct, kind), 0)
        decided: dict[tuple[str, str], tuple[str, int | None]] = {}
        for key in keys:
            decl = out.coverage_overrides.get(key)
            decided[key] = (decl.completeness.value, decl.expected_count) if decl else (
                manifest.coverage_default.value, None)

        cp = self.scans.get_checkpoint(scan_id, "persist_coverage")
        if not (cp and cp[1]):
            id_map = self.accounts.resolve_ids(manifest.platform, sorted({a for a, _ in keys}))
            rows = [CoverageRow(id_map[a], k, decided[(a, k)][0], keys[(a, k)], decided[(a, k)][1])
                    for (a, k) in sorted(keys) if a in id_map]
            # Overrides naming an account that never appears anywhere have no row to attach to.
            with self.db.transaction():
                self.edges.insert_coverage(scan_id, rows)
                self.scans.set_checkpoint(scan_id, "persist_coverage", len(rows), True)
        values = {c for c, _ in decided.values()}
        if not values:
            return Completeness.UNKNOWN.value
        if Completeness.PARTIAL.value in values:
            return Completeness.PARTIAL.value
        if Completeness.UNKNOWN.value in values:
            return Completeness.UNKNOWN.value
        return Completeness.COMPLETE.value

    # ------------------------------------------------------------------ graph (computed once per run)
    def _graph(self, scan_id: str, platform: str) -> _GraphState | None:
        if self._graph_state is not None or self._graph_error is not None:
            return self._graph_state
        gcfg = self.cfg.graph
        try:
            deadline = Deadline(gcfg.limits.max_seconds)
            g = build_graph(platform, self.edges.load_edges(scan_id), gcfg.limits)
            pairs, stats = neighbour_pairs(
                g, direction="out", min_degree=self.cfg.features.min_out_degree,
                min_shared=gcfg.feature_min_shared_targets, max_posting=gcfg.max_posting_list,
                limits=gcfg.limits, deadline=deadline)
            complete_following = {pid for (pid, kind), row in self.edges.load_coverage(scan_id).items()
                                  if kind == "following" and row.completeness == "complete"}
            self._graph_state = _GraphState(g, pairs, stats, node_metrics(
                g, pairs, self.cfg.features.min_out_degree, complete_following))
            self.scans.merge_detail(scan_id, {"graph": graph_summary(g), "similarity": stats})
        except GraphLimitExceeded as exc:
            self._graph_error = str(exc)
            self.scans.merge_detail(scan_id, {"graph_error": str(exc)})
            log.warning("graph analysis skipped", extra={"reason": str(exc)})
        return self._graph_state

    def _features_stage(self, scan_id: str, ref: datetime, out: ValidationOutcome) -> None:
        cp = self.scans.get_checkpoint(scan_id, "features")
        scan = self.scans.get_scan(scan_id)
        assert scan is not None
        gs = self._graph(scan_id, scan["platform"])
        if cp and cp[1]:
            return
        ids = self.accounts.scan_account_ids(scan_id)
        obs = self.accounts.load_observations(scan_id, ref)
        content_rows = self.content.load_content(scan_id)
        posts_by_author: dict[str, list[Post]] = {}
        for c in content_rows:
            posts_by_author.setdefault(c.author, []).append(
                Post(c.author, c.published_at.timestamp(), c.content_hash, c.simhash))
        coverage = self.edges.load_coverage(scan_id)
        comp_by_acct: dict[str, dict[str, str]] = {}
        for (pid, kind), row in coverage.items():
            comp_by_acct.setdefault(pid, {})[kind] = row.completeness
        content_collected = bool(content_rows)

        rows: list[FeatureRow] = []
        for pid in sorted(ids):
            nm = gs.metrics.get(pid) if gs else None
            ctx = AccountContext(
                public_id=pid, observations=obs.get(pid, []), posts=posts_by_author.get(pid, []),
                content_collected=content_collected,
                out_degree=nm.out_degree if nm else None, in_degree=nm.in_degree if nm else None,
                checkable_follows=nm.checkable_follows if nm else None,
                mutual_count=nm.mutual_count if nm else None,
                max_following_jaccard=nm.max_jaccard if nm else None,
                list_completeness=comp_by_acct.get(pid, {}))
            for f in compute_account_features(ctx, self.cfg.features, ref):
                rows.append(FeatureRow(ids[pid], f.name, f.category, f.value, f.unavailable_reason, f.details))
        self.analysis.replace_features(scan_id, FEATURE_VERSION, rows)
        self.scans.set_checkpoint(scan_id, "features", len(rows), True)

    def _rules_model_version(self) -> str:
        raw = self.cfg.raw
        config = {"scoring": raw["scoring"], "features": raw["features"], "feature_version": FEATURE_VERSION}
        return self.analysis.register_model_version(
            kind="rules", name="account-risk", version=self.cfg.version, config=config,
            config_sha256=jsonutil.sha256_hex(jsonutil.dumps(config)), feature_schema=dict(CATALOGUE))

    def _detection_stage(self, scan_id: str) -> None:
        cp = self.scans.get_checkpoint(scan_id, "detection")
        if cp and cp[1]:
            return
        model_id = self._rules_model_version()
        feats = self.analysis.load_features(scan_id, FEATURE_VERSION)
        rules = {r.feature: r for r in self.cfg.scoring.rules}
        rows: list[AssessmentRow] = []
        evidence: list[EvidenceRow] = []
        for pid in sorted(feats):
            fmap = {name: FeatureResult(name, d["value"], d["reason"], d["details"]) for name, d in feats[pid].items()}
            internal = next(iter(feats[pid].values()))["internal_id"]
            res = score_account(fmap, self.cfg.scoring)
            rows.append(AssessmentRow(internal, res.status, res.score, res.band, res.evidence_coverage,
                                      res.features_available, res.features_total, res.contributions,
                                      res.limitations))
            if res.status != "scored":
                continue  # no score means nothing "contributed"; the assessment's limitations explain why
            for c in res.contributions:
                if c["available"] and c["evidence"] > 0:
                    cat = CATALOGUE[c["feature"]]
                    ref: dict[str, str] = ({"table": "account_observations", "id": c["details"]["observation_id"]}
                                           if "observation_id" in c["details"] else
                                           {"table": "relationship_edges" if cat == "network" else "content_observations",
                                            "scan_id": scan_id, "account": pid})
                    evidence.append(EvidenceRow("account", internal, "account_feature",
                                                evidence_summary(c, rules[c["feature"]]),
                                                {"feature": c["feature"], "value": c["value"],
                                                 "evidence": c["evidence"], "weight": c["weight"],
                                                 "points": c["points"], "feature_details": c["details"]},
                                                [ref]))
        self.analysis.replace_assessments(scan_id, model_id, FEATURE_VERSION, rows)
        self.analysis.replace_evidence(scan_id, "account", model_id, evidence)
        self.scans.set_checkpoint(scan_id, "detection", len(rows), True)

    def _cluster_stage(self, scan_id: str, ref: datetime, out: ValidationOutcome) -> None:
        cp = self.scans.get_checkpoint(scan_id, "clusters")
        if cp and cp[1]:
            return
        scan = self.scans.get_scan(scan_id)
        assert scan is not None
        gcfg = self.cfg.graph
        cfg_blob = {"graph": self.cfg.raw["graph"], "simhash_max_distance": self.cfg.features.simhash_max_distance,
                    "method": METHOD, "method_version": METHOD_VERSION}
        model_id = self.analysis.register_model_version(
            kind="graph", name="coordinated-network", version=f"{METHOD}-{METHOD_VERSION}/{self.cfg.version}",
            config=cfg_blob, config_sha256=jsonutil.sha256_hex(jsonutil.dumps(cfg_blob)))
        gs = self._graph(scan_id, scan["platform"])
        if gs is None:  # graph limits were exceeded: record that there are no clusters, do not guess
            self.analysis.replace_clusters(scan_id, model_id, [])
            self.scans.set_checkpoint(scan_id, "clusters", 0, True)
            return
        deadline = Deadline(gcfg.limits.max_seconds)
        scores = {a["pid"]: a["score"] for a in self.analysis.list_assessments(scan_id)}
        posts = [Post(c.author, c.published_at.timestamp(), c.content_hash, c.simhash)
                 for c in self.content.load_content(scan_id)]
        observed = {pid for pid, history in self.accounts.load_observations(scan_id, ref).items() if history}
        cov = {k: v.completeness for k, v in self.edges.load_coverage(scan_id).items()}
        comms = detect_communities(gs.graph, gcfg.louvain_seed)
        result = detect_clusters(gs.graph, gs.pairs, posts, scores, observed, cov, node_community_index(comms),
                                 gcfg, deadline, self.cfg.features.simhash_max_distance)
        ids = self.accounts.scan_account_ids(scan_id)
        rows = [ClusterRow(
            members=[(ids[m], c.member_metrics[m]) for m in c.members], method=METHOD,
            method_version=METHOD_VERSION, metrics=c.metrics, signals=c.signals, coverage=c.coverage,
            signal_strength=c.signal_strength, confidence=c.confidence, uncertainty_notes=c.uncertainty_notes,
            alternative_explanations=c.alternative_explanations, evidence=c.evidence)
            for c in result.candidates]
        self.analysis.replace_clusters(scan_id, model_id, rows)
        self.scans.merge_detail(scan_id, {"clustering": {**result.stats, "communities_in_follow_graph": len(comms)}})
        self.scans.set_checkpoint(scan_id, "clusters", len(rows), True)

    # ------------------------------------------------------------------ summary
    def _summary(self, scan_id: str) -> dict[str, Any]:
        q = self.db.query_one
        one = lambda sql: int((q(sql, {"s": scan_id}) or {"n": 0})["n"])  # noqa: E731
        return {
            "accounts_in_scan": len(self.accounts.scan_account_ids(scan_id)),
            "accounts_with_profile_observation": one(
                "SELECT COUNT(DISTINCT platform_account_id) AS n FROM account_observations WHERE scan_id = :s"),
            "relationship_edges": one("SELECT COUNT(*) AS n FROM relationship_edges WHERE scan_id = :s"),
            "content_observations": one("SELECT COUNT(*) AS n FROM content_observations WHERE scan_id = :s"),
            "assessments_scored": one("SELECT COUNT(*) AS n FROM risk_assessments WHERE scan_id = :s AND status = 'scored'"),
            "assessments_insufficient_evidence": one(
                "SELECT COUNT(*) AS n FROM risk_assessments WHERE scan_id = :s AND status = 'insufficient_evidence'"),
            "candidate_clusters": one("SELECT COUNT(*) AS n FROM network_clusters WHERE scan_id = :s"),
            "quarantined_records": one("SELECT COUNT(*) AS n FROM quarantined_records WHERE scan_id = :s"),
        }


def import_dataset(db: Database, source: str | Path, cfg: Config, **kwargs: Any) -> ScanResult:
    """Convenience wrapper: run one dataset scan."""
    allow = bool(kwargs.pop("allow_resume_running", False))
    return DatasetScanRunner(db, cfg, **kwargs).run(source, allow_resume_running=allow)
