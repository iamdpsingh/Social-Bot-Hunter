"""Command line interface: ``python -m sbh <command>``.

Commands: migrate, capabilities, generate-demo, import, scans, report, diff, delete-scan,
retention-sweep, demo, docs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from sbh.config import load_config
from sbh.contracts.capabilities import default_registry, registry_markdown
from sbh.docgen import sync_docs
from sbh.graph.compare import diff_edge_sets
from sbh.pipeline.run import import_dataset
from sbh.shared.errors import SbhError, ScanFailedError
from sbh.shared.logging import configure_logging
from sbh.storage.analysis import AnalysisRepository
from sbh.storage.capabilities import sync_registry
from sbh.storage.database import Database, connect
from sbh.storage.edges import EdgeRepository
from sbh.storage.migrate import apply_migrations
from sbh.storage.retention import delete_scan, delete_scans_older_than
from sbh.storage.scans import ScanRepository


def _db_url(value: str | None) -> str:
    url = value or os.environ.get("SBH_DATABASE_URL") or "sqlite:///./sbh-dev.sqlite"
    return url if "://" in url else f"sqlite:///{url}"


def _open(args: argparse.Namespace) -> Database:
    db = connect(_db_url(args.db))
    apply_migrations(db)
    return db


def cmd_migrate(args: argparse.Namespace) -> int:
    db = connect(_db_url(args.db))
    applied = apply_migrations(db)
    n = sync_registry(db, default_registry())
    print(json.dumps({"migrations_applied": applied, "capabilities_synced": n}))
    return 0


def cmd_capabilities(args: argparse.Namespace) -> int:
    reg = default_registry()
    if args.markdown:
        print(registry_markdown(reg))
    else:
        for c in reg.all():
            print(f"{c.platform.value:10s} {c.operation.value:15s} {c.status.value:15s} supported={c.supported}")
    return 0


def cmd_generate_demo(args: argparse.Namespace) -> int:
    from sbh.fixtures import synthetic

    ds = synthetic.generate(args.seed)
    out = synthetic.write_csv_dir(ds, args.out)
    (Path(args.out).parent / f"{Path(args.out).name}.truth.json").write_text(
        json.dumps(ds.truth, indent=1, sort_keys=True), encoding="utf-8")
    print(f"wrote SYNTHETIC dataset to {out} (seed={args.seed})")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    db = _open(args)
    sync_registry(db, default_registry())
    cfg = load_config(args.config)
    try:
        res = import_dataset(db, args.source, cfg, requested_by=args.actor,
                             allow_resume_running=args.allow_resume_running)
    except ScanFailedError as exc:
        print(json.dumps({"scan_id": exc.scan_id, "status": "failed", "reason": exc.reason}), file=sys.stderr)
        return 2
    print(json.dumps({"scan_id": res.scan_id, "status": res.status, "already_imported": res.already_imported,
                      "summary": res.summary}, indent=2))
    return 0


def cmd_scans(args: argparse.Namespace) -> int:
    db = _open(args)
    for s in ScanRepository(db).list_scans(args.limit):
        print(f"{s['id']}  {s['status']:9s} {s['data_origin']:9s} {s['platform']:9s} "
              f"completeness={s['collection_completeness']} created={s['created_at']}")
    return 0


def _short(v: Any) -> str:
    return f"{v:.3g}" if isinstance(v, float) else str(v)


def cmd_report(args: argparse.Namespace) -> int:
    db = _open(args)
    scans, repo = ScanRepository(db), AnalysisRepository(db)
    scan = scans.get_scan(args.scan_id)
    if not scan:
        print(f"no such scan: {args.scan_id}", file=sys.stderr)
        return 1
    d = scan["status_detail"]
    label = "  *** SYNTHETIC DEMO DATA: no real accounts ***" if scan["data_origin"] == "synthetic" else ""
    print(f"Scan {scan['id']}{label}")
    print(f"  platform={scan['platform']} status={scan['status']} collection_completeness="
          f"{scan['collection_completeness']} config={scan['config_version']}")
    for r in d.get("partial_reasons", []):
        print(f"  partial because: {r}")
    for w in d.get("data_quality_warnings", []):
        print(f"  data-quality warning: {w}")
    if scan["failure_reason"]:
        print(f"  failure: {scan['failure_reason']}")
    print(f"  summary: {json.dumps(d.get('summary', {}))}")
    print("\nAccount risk (heuristic indicators, not proof of automation). Highest first:")
    shown = 0
    for a in repo.list_assessments(args.scan_id):
        if a["status"] != "scored":
            continue
        top = sorted((c for c in a["contributions"] if c.get("available") and c.get("points", 0) > 0),
                     key=lambda c: -c["points"])[:3]
        why = ", ".join(f"{c['feature']}={_short(c['value'])} (+{c['points']:.1f})" for c in top) or "none"
        print(f"  {a['pid']:8s} {a['score']:6.1f}  {a['band']:32s} coverage={a['evidence_coverage']:.0%}  top: {why}")
        shown += 1
        if shown >= args.top:
            break
    print("\nCandidate clusters (structure alone is NOT evidence of coordination):")
    for c in repo.list_clusters(args.scan_id):
        print(f"  {c['member_count']} accounts  signal_strength={c['signal_strength']}  confidence={c['confidence']}  "
              f"review={c['review_status']}")
        print(f"    members: {', '.join(c['members'][:12])}{' ...' if len(c['members']) > 12 else ''}")
        for name, sig in c["signals"].items():
            if isinstance(sig, dict):
                state = "present" if sig.get("signal_present") else ("not evaluated" if not sig.get("evaluated") else "absent")
                print(f"    {name}: {state}")
        for alt in c["alternative_explanations"]:
            print(f"    alternative: {alt}")
        for u in c["uncertainty_notes"][:2]:
            print(f"    uncertainty: {u}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    db = _open(args)
    er = EdgeRepository(db)
    cov_a = {k: v.completeness for k, v in er.load_coverage(args.scan_a).items()}
    cov_b = {k: v.completeness for k, v in er.load_coverage(args.scan_b).items()}
    d = diff_edge_sets(set(er.load_edges(args.scan_a)), set(er.load_edges(args.scan_b)), cov_a, cov_b)
    print(json.dumps(d.summary(), indent=2))
    print("confirmed_* are proven by a complete list; newly_observed / not_reobserved may only reflect "
          "different collection coverage.")
    return 0


def cmd_delete_scan(args: argparse.Namespace) -> int:
    counts = delete_scan(_open(args), args.scan_id, args.actor)
    print(json.dumps({"deleted": counts}, indent=2))
    return 0


def cmd_retention_sweep(args: argparse.Namespace) -> int:
    deleted = delete_scans_older_than(_open(args), args.days, args.actor)
    print(json.dumps({"deleted_scans": deleted}))
    return 0


def cmd_docs(args: argparse.Namespace) -> int:
    docs_dir = Path(args.docs_dir)
    stale = sync_docs(docs_dir, write=args.write)
    if stale and not args.write:
        print("generated documentation is out of date (run: python -m sbh docs --write):", file=sys.stderr)
        for line in stale:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("documentation updated" if stale else "generated documentation is current")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from sbh.fixtures import synthetic

    work = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="sbh-demo-"))
    ds = synthetic.generate(args.seed)
    src = synthetic.write_csv_dir(ds, work / "synthetic-demo")
    print(f"generated SYNTHETIC dataset in {src}")
    db = _open(args)
    sync_registry(db, default_registry())
    res = import_dataset(db, src, load_config(args.config), requested_by="demo")
    print(f"scan {res.scan_id}: {res.status}" + ("  (already imported)" if res.already_imported else ""))
    args.scan_id, args.top = res.scan_id, 12
    return cmd_report(args)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sbh", description="Social Bot Hunter")
    p.add_argument("--db", help="database URL or SQLite path (default: $SBH_DATABASE_URL or ./sbh-dev.sqlite)")
    p.add_argument("--config", help="detection config YAML (default: packaged rules-v1)")
    p.add_argument("-v", "--verbose", action="store_true", help="structured JSON logs on stderr")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("migrate", help="apply migrations and sync the capability registry").set_defaults(fn=cmd_migrate)
    c = sub.add_parser("capabilities", help="print the platform capability registry")
    c.add_argument("--markdown", action="store_true")
    c.set_defaults(fn=cmd_capabilities)
    g = sub.add_parser("generate-demo", help="write the synthetic demo dataset")
    g.add_argument("--out", required=True)
    g.add_argument("--seed", type=int, default=42)
    g.set_defaults(fn=cmd_generate_demo)
    i = sub.add_parser("import", help="import a dataset (CSV directory or JSON bundle) and analyse it")
    i.add_argument("source")
    i.add_argument("--actor", default="cli")
    i.add_argument("--allow-resume-running", action="store_true",
                   help="resume a scan marked running (only if you are sure no worker is alive)")
    i.set_defaults(fn=cmd_import)
    s = sub.add_parser("scans", help="list scans")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(fn=cmd_scans)
    r = sub.add_parser("report", help="text report for a scan")
    r.add_argument("scan_id")
    r.add_argument("--top", type=int, default=15)
    r.set_defaults(fn=cmd_report)
    d = sub.add_parser("diff", help="compare relationship snapshots of two scans")
    d.add_argument("scan_a")
    d.add_argument("scan_b")
    d.set_defaults(fn=cmd_diff)
    x = sub.add_parser("delete-scan", help="delete a scan and everything derived from it")
    x.add_argument("scan_id")
    x.add_argument("--actor", default="cli")
    x.set_defaults(fn=cmd_delete_scan)
    w = sub.add_parser("retention-sweep", help="delete finished scans older than N days")
    w.add_argument("--days", type=int, required=True)
    w.add_argument("--actor", default="retention-job")
    w.set_defaults(fn=cmd_retention_sweep)
    dd = sub.add_parser("docs", help="check (or --write) the generated tables in docs/")
    dd.add_argument("--docs-dir", default="docs")
    dd.add_argument("--write", action="store_true")
    dd.set_defaults(fn=cmd_docs)
    m = sub.add_parser("demo", help="generate synthetic data, import it, and print the report")
    m.add_argument("--workdir")
    m.add_argument("--seed", type=int, default=42)
    m.set_defaults(fn=cmd_demo)

    args = p.parse_args(argv)
    if args.verbose:
        configure_logging()
    try:
        return int(args.fn(args))
    except SbhError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
