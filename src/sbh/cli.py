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
from sbh.shared import jsonutil
from sbh.shared.errors import SbhError, ScanFailedError
from sbh.shared.logging import configure_logging
from sbh.storage.analysis import AnalysisRepository
from sbh.storage.capabilities import sync_registry
from sbh.storage.database import Database, connect
from sbh.storage.edges import EdgeRepository
from sbh.storage.migrate import apply_migrations
from sbh.storage.retention import delete_scan, delete_scans_older_than
from sbh.storage.scans import ScanRepository
from sbh.storage.users import UserRepository


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
            print(
                f"{c.platform.value:10s} {c.operation.value:15s} {c.status.value:15s} supported={c.supported}"
            )
    return 0


def cmd_generate_demo(args: argparse.Namespace) -> int:
    from sbh.fixtures import synthetic

    ds = synthetic.generate(args.seed)
    out = synthetic.write_csv_dir(ds, args.out)
    (Path(args.out).parent / f"{Path(args.out).name}.truth.json").write_text(
        json.dumps(ds.truth, indent=1, sort_keys=True), encoding="utf-8"
    )
    print(f"wrote SYNTHETIC dataset to {out} (seed={args.seed})")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    db = _open(args)
    sync_registry(db, default_registry())
    cfg = load_config(args.config)
    try:
        res = import_dataset(
            db,
            args.source,
            cfg,
            requested_by=args.actor,
            allow_resume_running=args.allow_resume_running,
        )
    except ScanFailedError as exc:
        print(
            json.dumps({"scan_id": exc.scan_id, "status": "failed", "reason": exc.reason}),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "scan_id": res.scan_id,
                "status": res.status,
                "already_imported": res.already_imported,
                "summary": res.summary,
            },
            indent=2,
        )
    )
    return 0


def cmd_scans(args: argparse.Namespace) -> int:
    db = _open(args)
    for s in ScanRepository(db).list_scans(args.limit):
        print(
            f"{s['id']}  {s['status']:9s} {s['data_origin']:9s} {s['platform']:9s} "
            f"completeness={s['collection_completeness']} created={s['created_at']}"
        )
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
    label = (
        "  *** SYNTHETIC DEMO DATA: no real accounts ***"
        if scan["data_origin"] == "synthetic"
        else ""
    )
    print(f"Scan {scan['id']}{label}")
    print(
        f"  platform={scan['platform']} status={scan['status']} collection_completeness="
        f"{scan['collection_completeness']} config={scan['config_version']}"
    )
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
        top = sorted(
            (c for c in a["contributions"] if c.get("available") and c.get("points", 0) > 0),
            key=lambda c: -c["points"],
        )[:3]
        why = (
            ", ".join(f"{c['feature']}={_short(c['value'])} (+{c['points']:.1f})" for c in top)
            or "none"
        )
        print(
            f"  {a['pid']:8s} {a['score']:6.1f}  {a['band']:32s} coverage={a['evidence_coverage']:.0%}  top: {why}"
        )
        shown += 1
        if shown >= args.top:
            break
    print("\nCandidate clusters (structure alone is NOT evidence of coordination):")
    for c in repo.list_clusters(args.scan_id):
        print(
            f"  {c['member_count']} accounts  signal_strength={c['signal_strength']}  confidence={c['confidence']}  "
            f"review={c['review_status']}"
        )
        print(
            f"    members: {', '.join(c['members'][:12])}{' ...' if len(c['members']) > 12 else ''}"
        )
        for name, sig in c["signals"].items():
            if isinstance(sig, dict):
                state = (
                    "present"
                    if sig.get("signal_present")
                    else ("not evaluated" if not sig.get("evaluated") else "absent")
                )
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
    d = diff_edge_sets(
        set(er.load_edges(args.scan_a)), set(er.load_edges(args.scan_b)), cov_a, cov_b
    )
    print(json.dumps(d.summary(), indent=2))
    print(
        "confirmed_* are proven by a complete list; newly_observed / not_reobserved may only reflect "
        "different collection coverage."
    )
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
        print(
            "generated documentation is out of date (run: python -m sbh docs --write):",
            file=sys.stderr,
        )
        for line in stale:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("documentation updated" if stale else "generated documentation is current")
    return 0


def cmd_quarantine_list(args: argparse.Namespace) -> int:
    db = _open(args)
    repo = ScanRepository(db)
    summary = repo.quarantine_summary(args.scan_id)
    records = repo.list_quarantined_records(
        args.scan_id, entity=args.entity, kind=args.kind, limit=args.limit, offset=args.offset
    )
    if getattr(args, "json", False):
        print(json.dumps({"summary": summary, "records": records}, indent=2, default=str))
        return 0
    print(f"Quarantine summary for scan {args.scan_id}:")
    if summary:
        print("  " + ", ".join(f"{s['entity']}:{s['kind']}={s['n']}" for s in summary))
    else:
        print("  No quarantined records found.")
        return 0
    print(f"\nShowing {len(records)} record(s):")
    for r in records:
        reasons_str = ", ".join(r["reasons"])
        print(
            f"  [{r['id'][:8]}] entity={r['entity']} kind={r['kind']} ref={r['source_ref']} reasons={reasons_str}"
        )
    return 0


def cmd_quarantine_inspect(args: argparse.Namespace) -> int:
    db = _open(args)
    repo = ScanRepository(db)
    rec = repo.get_quarantined_record(args.record_id)
    if not rec:
        print(f"quarantined record not found: {args.record_id}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(json.dumps(rec, indent=2, default=str))
        return 0
    print(f"Quarantined Record: {rec['id']}")
    print(f"  Scan ID:     {rec['scan_id']}")
    print(f"  Entity:      {rec['entity']}")
    print(f"  Kind:        {rec['kind']}")
    print(f"  Source Ref:  {rec['source_ref']}")
    print(f"  Reasons:     {', '.join(rec['reasons'])}")
    print(f"  Created At:  {rec['created_at']}")
    print("  Raw Payload:")
    for k, v in rec["raw"].items():
        print(f"    {k}: {v}")
    return 0


def cmd_create_user(args: argparse.Namespace) -> int:
    from services.api.auth import hash_password

    db = _open(args)
    repo = UserRepository(db)
    hashed = hash_password(args.password)
    try:
        user = repo.create_user(
            username=args.username,
            hashed_password=hashed,
            role=args.role,
            full_name=args.full_name,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(jsonutil.dumps(user))
    else:
        print(f"Created user '{user['username']}' with role '{user['role']}' (ID: {user['id']})")
    return 0


def cmd_list_users(args: argparse.Namespace) -> int:
    db = _open(args)
    repo = UserRepository(db)
    users = repo.list_users(limit=args.limit, offset=args.offset)
    if args.json:
        print(jsonutil.dumps(users))
    else:
        print(f"{'USERNAME':<20} {'ROLE':<15} {'ACTIVE':<8} {'FULL NAME':<25} {'ID'}")
        print("-" * 80)
        for u in users:
            print(
                f"{u['username']:<20} {u['role']:<15} {str(bool(u['is_active'])):<8} "
                f"{str(u.get('full_name') or ''):<25} {u['id']}"
            )
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
    print(
        f"scan {res.scan_id}: {res.status}"
        + ("  (already imported)" if res.already_imported else "")
    )
    args.scan_id, args.top = res.scan_id, 12
    return cmd_report(args)



def cmd_runtime_status(args: argparse.Namespace) -> int:
    from sbh.runtime.supervisor import LocalSupervisor
    s = LocalSupervisor()
    st = s.get_status()
    if args.json:
        print(json.dumps(st, indent=2))
    else:
        print("=== Social Bot Hunter Runtime Status ===")
        print(f"Supervisor PID: {st['supervisor_pid']} | Uptime: {st['uptime_seconds']}s")
        print("Services:")
        for name, info in st["services"].items():
            print(f"  - {name:12s}: state={info['state']} pid={info['pid']} port={info.get('port')}")
        print("Queue:")
        for q_state, cnt in st["queue"].items():
            print(f"  - {q_state:12s}: {cnt}")
        print("Storage:")
        for cat, sinfo in st["storage"].items():
            print(f"  - {cat:12s}: {sinfo['file_count']} files ({sinfo['total_mb']} MB)")
    return 0


def cmd_runtime_check_env(args: argparse.Namespace) -> int:
    from sbh.runtime.env_validator import validate_local_runtime_environment
    rep = validate_local_runtime_environment(check_ports=not args.no_ports)
    if args.json:
        print(json.dumps(rep.to_dict(), indent=2))
    else:
        print(f"=== Local Runtime Environment Audit ({'PASSED' if rep.all_passed else 'WARNINGS'}) ===")
        print(f"Base Directory: {rep.base_dir}")
        print(f"Python: {rep.python_path} (venv={rep.virtual_env_active})")
        print("Checks:")
        for c in rep.checks:
            badge = "[OK]  " if c.passed else "[WARN]"
            print(f"  {badge} {c.name:25s}: {c.message}")
    return 0 if rep.all_passed else 1


def cmd_storage_stats(args: argparse.Namespace) -> int:
    from sbh.storage.fs import LocalStorageManager, StorageCategory
    mgr = LocalStorageManager()
    stats = {cat.value: mgr.get_directory_stats(cat).to_dict() for cat in StorageCategory}
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print("=== Local Storage Allocation ===")
        for cat, info in stats.items():
            print(f"  - {cat:12s}: {info['file_count']:4d} files | {info['total_mb']:8.2f} MB ({info['path']})")
    return 0


def cmd_storage_prune(args: argparse.Namespace) -> int:
    from sbh.storage.fs import LocalStorageManager, StorageCategory
    from sbh.storage.retention_engine import RetentionPolicy, StorageRetentionEngine
    mgr = LocalStorageManager()
    engine = StorageRetentionEngine(mgr)
    policy = RetentionPolicy(
        max_age_days=args.max_age_days,
        max_directory_bytes=args.max_size_mb * 1024 * 1024 if args.max_size_mb else None,
        keep_minimum_count=args.keep_minimum,
    )
    if args.category:
        cat = StorageCategory(args.category)
        rep = engine.prune_category(cat, policy, dry_run=args.dry_run)
        reports = [rep]
    else:
        reports = engine.prune_all({cat: policy for cat in StorageCategory}, dry_run=args.dry_run)

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    else:
        mode = "[DRY-RUN] " if args.dry_run else ""
        print(f"=== {mode}Storage Retention Prune ===")
        for r in reports:
            print(f"  - {r.category:12s}: deleted {r.deleted_count} files | reclaimed {r.reclaimed_mb} MB (preserved {r.preserved_count})")
    return 0


def cmd_storage_verify(args: argparse.Namespace) -> int:
    from sbh.storage.fs import LocalStorageManager, StorageCategory
    from sbh.storage.manifest import AssetManifestManager
    mgr = LocalStorageManager()
    manifest = AssetManifestManager(mgr)
    cat = StorageCategory(args.category) if args.category else None
    assets = manifest.list_assets(category=cat)
    failures = 0
    print(f"=== Verifying {len(assets)} storage assets ===")
    for a in assets:
        ok, msg = manifest.verify_tamper(a.asset_id)
        if not ok:
            failures += 1
            print(f"  [FAIL] {a.asset_id}: {msg}")
        else:
            if args.verbose:
                print(f"  [OK]   {a.asset_id}: {msg}")
    print(f"Verification complete: {len(assets) - failures} passed, {failures} failed")
    return 1 if failures > 0 else 0


def cmd_db_backup(args: argparse.Namespace) -> int:
    from sbh.storage.backup import DatabaseBackupEngine
    from sbh.storage.fs import LocalStorageManager
    mgr = LocalStorageManager()
    engine = DatabaseBackupEngine(mgr)
    db_p = Path(args.db if args.db else "sbh-dev.sqlite")
    if not db_p.exists():
        print(f"Error: Database file does not exist: {db_p}", file=sys.stderr)
        return 1
    bak_path, meta = engine.backup_sqlite(db_p, output_filename=args.output, compress=args.compress, notes=args.notes)
    if args.json:
        print(json.dumps(meta.to_dict(), indent=2))
    else:
        print(f"Backup created successfully: {bak_path}")
        print(f"  ID: {meta.backup_id} | Size: {meta.size_bytes} bytes | SHA-256: {meta.sha256}")
        print(f"  Tables backed up: {len(meta.table_counts)}")
    return 0


def cmd_db_restore(args: argparse.Namespace) -> int:
    from sbh.storage.fs import LocalStorageManager
    from sbh.storage.restore import DatabaseRestoreEngine
    mgr = LocalStorageManager()
    engine = DatabaseRestoreEngine(mgr)
    bak_p = Path(args.input)
    target_p = Path(args.db if args.db else "sbh-dev.sqlite")
    if not bak_p.exists():
        print(f"Error: Backup file not found: {bak_p}", file=sys.stderr)
        return 1
    res = engine.restore_sqlite(bak_p, target_p, create_safety_backup=not args.no_safety)
    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
    else:
        if res.success:
            print(f"Database restored successfully into {res.target_db} ({res.duration_seconds}s)")
            if res.safety_backup_path:
                print(f"  Safety snapshot saved at: {res.safety_backup_path}")
            print(f"  Restored {len(res.restored_tables)} tables")
        else:
            print(f"Restore failed: {res.error}", file=sys.stderr)
            return 1
    return 0


def cmd_db_verify(args: argparse.Namespace) -> int:
    from sbh.storage.db_verify import verify_backup_integrity, verify_sqlite_database
    p = Path(args.path)
    if not p.exists():
        print(f"Error: Path does not exist: {p}", file=sys.stderr)
        return 1

    if p.name.endswith(".meta.json") or p.name.endswith(".bak") or p.name.endswith(".gz"):
        ok, msg = verify_backup_integrity(p)
        print(f"Backup verification: {'PASSED' if ok else 'FAILED'} - {msg}")
        return 0 if ok else 1

    rep = verify_sqlite_database(p)
    if args.json:
        print(json.dumps(rep.to_dict(), indent=2))
    else:
        print(f"SQLite Verification ({p}): {'VALID' if rep.is_valid else 'CORRUPT'}")
        print(f"  Integrity Check: {'OK' if rep.integrity_check_passed else 'FAILED'}")
        print(f"  Foreign Keys: {'OK' if rep.foreign_keys_valid else 'FAILED'}")
        print(f"  Tables ({rep.table_count}): {', '.join(rep.tables)}")
        if rep.errors:
            print(f"  Errors: {', '.join(rep.errors)}")
    return 0 if rep.is_valid else 1


def cmd_worker_run(args: argparse.Namespace) -> int:
    from sbh.runtime.worker import LocalWorker
    worker = LocalWorker()
    print(f"Starting local background worker [{worker.worker_id}]...")
    n = worker.run_loop(poll_interval=args.poll_interval, max_jobs=args.max_jobs)
    print(f"Worker shutdown. Processed {n} tasks.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sbh", description="Social Bot Hunter")
    p.add_argument(
        "--db", help="database URL or SQLite path (default: $SBH_DATABASE_URL or ./sbh-dev.sqlite)"
    )
    p.add_argument("--config", help="detection config YAML (default: packaged rules-v1)")
    p.add_argument("-v", "--verbose", action="store_true", help="structured JSON logs on stderr")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "migrate", help="apply migrations and sync the capability registry"
    ).set_defaults(fn=cmd_migrate)
    c = sub.add_parser("capabilities", help="print the platform capability registry")
    c.add_argument("--markdown", action="store_true")
    c.set_defaults(fn=cmd_capabilities)
    g = sub.add_parser("generate-demo", help="write the synthetic demo dataset")
    g.add_argument("--out", required=True)
    g.add_argument("--seed", type=int, default=42)
    g.set_defaults(fn=cmd_generate_demo)
    i = sub.add_parser(
        "import", help="import a dataset (CSV directory or JSON bundle) and analyse it"
    )
    i.add_argument("source")
    i.add_argument("--actor", default="cli")
    i.add_argument(
        "--allow-resume-running",
        action="store_true",
        help="resume a scan marked running (only if you are sure no worker is alive)",
    )
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

    ql = sub.add_parser("quarantine-list", help="list quarantined records for a scan")
    ql.add_argument("scan_id")
    ql.add_argument("--entity", choices=["account", "relationship", "content"])
    ql.add_argument("--kind", choices=["invalid", "duplicate"])
    ql.add_argument("--limit", type=int, default=50)
    ql.add_argument("--offset", type=int, default=0)
    ql.add_argument("--json", action="store_true", help="output JSON")
    ql.set_defaults(fn=cmd_quarantine_list)

    qi = sub.add_parser("quarantine-inspect", help="inspect details of a quarantined record")
    qi.add_argument("record_id")
    qi.add_argument("--json", action="store_true", help="output JSON")
    qi.set_defaults(fn=cmd_quarantine_inspect)

    cu = sub.add_parser("create-user", help="create a user account")
    cu.add_argument("username")
    cu.add_argument("password")
    cu.add_argument(
        "--role", required=True, choices=["admin", "investigator", "auditor", "readonly"]
    )
    cu.add_argument("--full-name", default=None)
    cu.add_argument("--json", action="store_true")
    cu.set_defaults(fn=cmd_create_user)

    lu = sub.add_parser("list-users", help="list user accounts")
    lu.add_argument("--limit", type=int, default=50)
    lu.add_argument("--offset", type=int, default=0)
    lu.add_argument("--json", action="store_true")
    lu.set_defaults(fn=cmd_list_users)

    dd = sub.add_parser("docs", help="check (or --write) the generated tables in docs/")
    dd.add_argument("--docs-dir", default="docs")
    dd.add_argument("--write", action="store_true")
    dd.set_defaults(fn=cmd_docs)
    m = sub.add_parser("demo", help="generate synthetic data, import it, and print the report")
    m.add_argument("--workdir")
    m.add_argument("--seed", type=int, default=42)
    m.set_defaults(fn=cmd_demo)

    
    # Day 12 runtime and storage commands
    rts = sub.add_parser("runtime-status", help="show local multi-service supervisor and resource telemetry")
    rts.add_argument("--json", action="store_true")
    rts.set_defaults(fn=cmd_runtime_status)

    rtc = sub.add_parser("runtime-check-env", help="audit local virtual environment and system dependencies")
    rtc.add_argument("--no-ports", action="store_true", help="skip port occupation checks")
    rtc.add_argument("--json", action="store_true")
    rtc.set_defaults(fn=cmd_runtime_check_env)

    sts = sub.add_parser("storage-stats", help="show local disk consumption breakdown for snapshots, models, exports")
    sts.add_argument("--json", action="store_true")
    sts.set_defaults(fn=cmd_storage_stats)

    stp = sub.add_parser("storage-prune", help="enforce retention policy cleanup on storage directories")
    stp.add_argument("--category", choices=["snapshots", "models", "exports", "backups", "temp"])
    stp.add_argument("--max-age-days", type=int, default=30)
    stp.add_argument("--max-size-mb", type=float, default=None)
    stp.add_argument("--keep-minimum", type=int, default=3)
    stp.add_argument("--dry-run", action="store_true")
    stp.add_argument("--json", action="store_true")
    stp.set_defaults(fn=cmd_storage_prune)

    stv = sub.add_parser("storage-verify", help="verify cryptographic hashes of assets against manifest")
    stv.add_argument("--category", choices=["snapshots", "models", "exports", "backups", "temp"])
    stv.set_defaults(fn=cmd_storage_verify)

    dbb = sub.add_parser("db-backup", help="create verified atomic database snapshot")
    dbb.add_argument("--db", help="path to source database file")
    dbb.add_argument("--output", help="custom output backup filename")
    dbb.add_argument("--compress", action="store_true", help="gzip compress backup artifact")
    dbb.add_argument("--notes", help="optional description notes for metadata")
    dbb.add_argument("--json", action="store_true")
    dbb.set_defaults(fn=cmd_db_backup)

    dbr = sub.add_parser("db-restore", help="safely restore database from backup artifact")
    dbr.add_argument("--input", required=True, help="path to backup artifact (.db or .db.gz)")
    dbr.add_argument("--db", help="target database file to replace")
    dbr.add_argument("--no-safety", action="store_true", help="skip pre-restore safety snapshot")
    dbr.add_argument("--json", action="store_true")
    dbr.set_defaults(fn=cmd_db_restore)

    dbv = sub.add_parser("db-verify", help="verify SQLite integrity or backup manifest checksum")
    dbv.add_argument("path", help="path to database or backup artifact")
    dbv.add_argument("--json", action="store_true")
    dbv.set_defaults(fn=cmd_db_verify)

    wkr = sub.add_parser("worker-run", help="run local background worker processing queue jobs")
    wkr.add_argument("--poll-interval", type=float, default=0.5)
    wkr.add_argument("--max-jobs", type=int, default=None)
    wkr.set_defaults(fn=cmd_worker_run)

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
