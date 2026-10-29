"""Generate the machine-derivable parts of the documentation, and check they are current.

Hand-written prose lives in docs/*.md; tables derived from code (schema, capability registry,
scoring rules) sit between ``<!-- BEGIN GENERATED:name -->`` and ``<!-- END GENERATED:name -->``
markers. ``sbh docs`` fails if they differ from what the code produces, so the documentation
cannot silently go stale.
"""

from __future__ import annotations

import re
from pathlib import Path

from sbh.config import Config, load_config
from sbh.contracts.capabilities import default_registry, registry_markdown
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations

TABLE_DOCS: dict[str, tuple[str, str, str]] = {
    # table: (purpose, grain, retention)
    "scan_jobs": ("One investigation run: its mode, status, completeness and outcome detail.",
                  "one row per scan", "Deleted with the scan (`sbh delete-scan`)."),
    "dataset_imports": ("Provenance of an imported dataset; its content hash makes imports idempotent.",
                        "one row per imported input (unique content hash)", "Deleted with the scan."),
    "scan_checkpoints": ("Restart points: how far each write stage got.",
                         "one row per (scan, stage)", "Deleted with the scan."),
    "quarantined_records": ("Rows rejected (or exact duplicates dropped) during validation, with reasons. Post text is never kept.",
                            "one row per rejected input row", "Deleted with the scan."),
    "platform_accounts": ("Stable identity of an account on one platform. Usernames are mutable attributes, not identity.",
                          "one row per (platform, platform_account_id)",
                          "Removed when no remaining scan references the account."),
    "account_observations": ("What was observed about an account at a point in time. NULL means not observed; 0 is a real zero.",
                             "one row per (account, scan, observed_at)", "Deleted with the scan."),
    "relationship_edges": ("A directed 'source follows target' relationship observed by a scan. The reverse is never inferred.",
                           "one row per (scan, source, target, type)", "Deleted with the scan."),
    "relationship_list_coverage": ("Whether an observed followers/following list is the complete list. Separates confirmed change from incomplete collection.",
                                   "one row per (scan, account, list kind)", "Deleted with the scan."),
    "content_observations": ("Post fingerprints and counts. Raw post text is never stored.",
                             "one row per (scan, platform, content id)", "Deleted with the scan."),
    "model_versions": ("Immutable record of the rules/graph configuration that produced stored results.",
                       "one row per (kind, name, version)", "Kept (configuration, not personal data)."),
    "account_features": ("Interpretable per-account signals. Unavailable features have no value and a reason.",
                         "one row per (scan, account, feature, feature version)", "Deleted with the scan."),
    "risk_assessments": ("Explainable heuristic risk result, or an insufficient-evidence result with no score.",
                         "one row per (scan, account, model version, feature version)", "Deleted with the scan."),
    "network_clusters": ("A candidate group of accounts with signals, coverage, uncertainty and alternative explanations.",
                         "one row per detected cluster per scan", "Deleted with the scan."),
    "cluster_memberships": ("Which accounts belong to which candidate cluster, with member-level metrics.",
                            "one row per (cluster, account)", "Deleted with the scan."),
    "evidence_records": ("Human-readable evidence behind a score or cluster, with references to source rows.",
                         "one row per piece of evidence", "Deleted with the scan."),
    "platform_capabilities": ("Persisted capability registry: what each platform operation supports and how far that is verified.",
                              "one row per (platform, operation)", "Kept (configuration)."),
    "audit_events": ("Security-relevant actions: scan lifecycle, rejected imports, deletions.",
                     "one row per event", "Kept; contains no deleted content."),
}

COLUMN_NOTES: dict[tuple[str, str], str] = {
    ("scan_jobs", "status"): "pending, running, complete, partial, failed, cancelled, awaiting_access_approval",
    ("scan_jobs", "collection_completeness"): "Are the observed relationship lists known to be whole? complete / partial / unknown",
    ("scan_jobs", "reference_time"): "When the data was collected (manifest `collected_at`); used for freshness and reproducible re-analysis",
    ("scan_jobs", "data_origin"): "synthetic, imported or api; synthetic scans are labelled as demo data everywhere",
    ("scan_jobs", "status_detail"): "JSON: summary counts, partial reasons, data-quality warnings, graph stats",
    ("dataset_imports", "content_sha256"): "SHA-256 over the input bytes: the idempotency key",
    ("quarantined_records", "kind"): "invalid (rejected) or duplicate (exact duplicate, harmless)",
    ("platform_accounts", "first_seen_scan_id"): "NULL after that scan is deleted",
    ("account_observations", "observed_at"): "When the platform state was observed (source time)",
    ("account_observations", "collected_at"): "When it was collected (scan reference time)",
    ("account_observations", "account_created_at"): "Only if the source supplied it; never inferred",
    ("account_observations", "is_verified"): "Stored for context only; never used as proof of anything",
    ("account_observations", "source_payload_sha256"): "Hash of the raw input row (the row itself is not stored)",
    ("relationship_edges", "verification_status"): "unverified, source_asserted or cross_checked",
    ("relationship_list_coverage", "expected_count"): "Total the source claimed, if any; a mismatch downgrades 'complete'",
    ("content_observations", "simhash"): "64-bit near-duplicate fingerprint, 16 hex characters",
    ("content_observations", "content_hash"): "SHA-256 of normalised text, or a source-supplied hash when no text was given",
    ("account_features", "value"): "NULL iff the feature is unavailable (enforced by a CHECK constraint)",
    ("risk_assessments", "score"): "0-100 heuristic indicator, NULL when evidence is insufficient (CHECK-enforced)",
    ("risk_assessments", "evidence_coverage"): "Available rule weight divided by total rule weight",
    ("risk_assessments", "contributions"): "JSON: every rule with value, evidence, weight and score points, or why unavailable",
    ("network_clusters", "signal_strength"): "low = structure only; moderate/high = one/two or more independent behavioural signals",
    ("network_clusters", "confidence"): "Capped by data coverage; automation never sets 'high'",
    ("network_clusters", "review_status"): "Human review state; starts as unreviewed",
    ("evidence_records", "subject_id"): "platform_accounts.id or network_clusters.id depending on subject_type (no FK: polymorphic)",
    ("model_versions", "config_sha256"): "Reusing a version with different configuration is refused",
    ("platform_capabilities", "status"): "implemented, verified, requires_approval, unsupported, temporarily_unavailable, not_configured",
    ("platform_capabilities", "supported"): "NULL = not yet established from official documentation",
    ("audit_events", "actor"): "'cli' or a service name today; user ids once authentication exists",
}


def data_dictionary_markdown() -> str:
    db = SQLiteDatabase()
    apply_migrations(db)
    tables = [r["name"] for r in db.query_all(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name <> 'schema_migrations' ORDER BY rowid")]
    out: list[str] = []
    for t in tables:
        purpose, grain, retention = TABLE_DOCS[t]
        fks = {r["from"]: f"{r['table']}.{r['to']}" for r in db.query_all(f"PRAGMA foreign_key_list({t})")}
        uniques: set[str] = set()
        for idx in db.query_all(f"PRAGMA index_list({t})"):
            if idx["unique"] and idx["origin"] in ("u", "pk"):
                cols = [c["name"] for c in db.query_all(f"PRAGMA index_info({idx['name']})")]
                if len(cols) == 1:
                    uniques.add(cols[0])
        out += [f"### `{t}`", "", purpose, "", f"- **Grain:** {grain}", f"- **Retention:** {retention}", "",
                "| Column | Type | Null | Notes |", "|---|---|---|---|"]
        for c in db.query_all(f"PRAGMA table_info({t})"):
            notes = []
            if c["pk"]:
                notes.append("primary key")
            if c["name"] in fks:
                notes.append(f"FK -> {fks[c['name']]}")
            if c["name"] in uniques and not c["pk"]:
                notes.append("unique")
            if (t, c["name"]) in COLUMN_NOTES:
                notes.append(COLUMN_NOTES[(t, c["name"])])
            out.append(f"| `{c['name']}` | {c['type']} | {'no' if c['notnull'] or c['pk'] else 'yes'} | {'; '.join(notes)} |")
        out.append("")
    db.close()
    return "\n".join(out).rstrip()


def rules_markdown(cfg: Config | None = None) -> str:
    cfg = cfg or load_config()
    total = sum(r.weight for r in cfg.scoring.rules)
    rows = ["| Feature | Weight | Share | Evidence 0 at | Evidence 1 at | What it measures |", "|---|---|---|---|---|---|"]
    for r in cfg.scoring.rules:
        rows.append(f"| `{r.feature}` | {r.weight:g} | {r.weight / total:.1%} | {r.zero_at:g} | {r.full_at:g} | {r.description} |")
    rows += ["", f"Configuration version `{cfg.version}`; minimum {cfg.scoring.min_features} available rules and "
             f"{cfg.scoring.min_weight_coverage:.0%} weight coverage, otherwise the result is `insufficient_evidence`.", "",
             "| Band (score at least) | Label |", "|---|---|"]
    rows += [f"| {b.lower:g} | `{b.label}` |" for b in cfg.scoring.bands]
    return "\n".join(rows)


GENERATORS = {
    "capabilities": ("platform-access-matrix.md", lambda: registry_markdown(default_registry())),
    "data-dictionary": ("data-dictionary.md", data_dictionary_markdown),
    "scoring-rules": ("detection-methodology.md", rules_markdown),
}


def _block(name: str, body: str) -> str:
    return f"<!-- BEGIN GENERATED:{name} -->\n{body}\n<!-- END GENERATED:{name} -->"


def sync_docs(docs_dir: Path, write: bool) -> list[str]:
    """Return the names of out-of-date generated blocks; rewrite them when ``write`` is true."""
    stale: list[str] = []
    for name, (filename, generate) in GENERATORS.items():
        path = docs_dir / filename
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        pattern = re.compile(rf"<!-- BEGIN GENERATED:{re.escape(name)} -->.*?<!-- END GENERATED:{re.escape(name)} -->", re.S)
        if not pattern.search(text):
            stale.append(f"{filename}: missing GENERATED:{name} markers")
            continue
        fresh = _block(name, generate())
        if pattern.search(text).group(0) != fresh:  # type: ignore[union-attr]
            stale.append(f"{filename}: GENERATED:{name} is out of date")
            if write:
                path.write_text(pattern.sub(lambda _m, fresh=fresh: fresh, text), encoding="utf-8")
    return stale
