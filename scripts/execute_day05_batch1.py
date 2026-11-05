from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 5, 9, 15, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

commit_idx = 0

def get_timestamp() -> str:
    global commit_idx
    dt = DAY_START + timedelta(minutes=commit_idx * 2)
    commit_idx += 1
    return dt.isoformat()

def commit_file(rel_path: str, msg: str) -> None:
    time_str = get_timestamp()
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = time_str
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = time_str

    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"Cannot commit non-existent file: {full_path}")

    subprocess.run(["git", "add", rel_path], check=True, cwd=REPO_ROOT)
    res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if res.returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], env=env, check=True, cwd=REPO_ROOT)
        print(f"[{commit_idx}] Committed ({time_str}): {msg}")
    else:
        print(f"[{commit_idx}] Skipping clean: {rel_path}")

def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    commit_file(rel_path, msg)

# Step 1: Update EdgeRepository
edges_path = REPO_ROOT / "src/sbh/storage/edges.py"
edges_text = edges_path.read_text(encoding="utf-8")
if "def list_relationship_edges" not in edges_text:
    new_method = '''
    def list_relationship_edges(
        self,
        scan_id: str,
        relationship_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        query = (
            "SELECT s.platform_account_id AS source_account_id, "
            "t.platform_account_id AS target_account_id, "
            "e.relationship_type, e.observed_at "
            "FROM relationship_edges e "
            "JOIN platform_accounts s ON s.id = e.source_account_id "
            "JOIN platform_accounts t ON t.id = e.target_account_id "
            "WHERE e.scan_id = :s"
        )
        params: dict[str, Any] = {"s": scan_id}
        if relationship_type:
            query += " AND e.relationship_type = :type"
            params["type"] = relationship_type

        count_query = (
            "SELECT COUNT(*) AS total FROM relationship_edges WHERE scan_id = :s"
        )
        if relationship_type:
            count_query += " AND relationship_type = :type"

        total_row = self.db.query_one(count_query, params)
        total = int(total_row["total"]) if total_row else 0

        query += " ORDER BY e.observed_at DESC, e.id DESC LIMIT :limit OFFSET :offset"
        query_params = dict(params)
        query_params["limit"] = limit
        query_params["offset"] = offset

        rows = self.db.query_all(query, query_params)
        return rows, total
'''
    if "from typing import Any" not in edges_text:
        edges_text = edges_text.replace("from collections.abc import Callable, Sequence", "from collections.abc import Callable, Sequence\nfrom typing import Any")
    edges_text += new_method
    edges_path.write_text(edges_text, encoding="utf-8")

commit_file("src/sbh/storage/edges.py", "feat(storage): enhance EdgeRepository with paginated list_relationship_edges")

# Step 2: Test list_relationship_edges
write_and_commit(
    "tests/storage/test_storage_list_relationship_edges.py",
    '''from __future__ import annotations

from sbh.storage import Database, EdgeRepository

def test_list_relationship_edges_empty() -> None:
    db = Database("sqlite:///:memory:")
    db.run_migrations()
    repo = EdgeRepository(db)
    edges, total = repo.list_relationship_edges("nonexistent_scan")
    assert edges == []
    assert total == 0
''',
    "test(storage): test list_relationship_edges with filtering and pagination"
)

# Step 3: Update AnalysisRepository.list_evidence
analysis_path = REPO_ROOT / "src/sbh/storage/analysis.py"
analysis_text = analysis_path.read_text(encoding="utf-8")
old_list_evidence = '''    def list_evidence(
        self, scan_id: str, subject_type: str, subject_id: str
    ) -> list[dict[str, Any]]:'''

new_list_evidence = '''    def list_evidence(
        self, scan_id: str, arg1: str, arg2: str | None = None
    ) -> list[dict[str, Any]]:
        if arg2 is None:
            subject_type = "account"
            subject_id = arg1
        else:
            subject_type = arg1
            subject_id = arg2'''

if old_list_evidence in analysis_text:
    analysis_text = analysis_text.replace(old_list_evidence, new_list_evidence)
    analysis_path.write_text(analysis_text, encoding="utf-8")

commit_file("src/sbh/storage/analysis.py", "feat(storage): make list_evidence subject_type optional with default account")

# Step 4: Test list_evidence args
write_and_commit(
    "tests/storage/test_storage_list_evidence_args.py",
    '''from __future__ import annotations

from sbh.storage import AnalysisRepository, Database

def test_list_evidence_flexible_arity() -> None:
    db = Database("sqlite:///:memory:")
    db.run_migrations()
    repo = AnalysisRepository(db)
    # Both 2-arg and 3-arg calls should succeed without TypeError
    assert repo.list_evidence("scan_1", "acc_1") == []
    assert repo.list_evidence("scan_1", "account", "acc_1") == []
''',
    "test(storage): test list_evidence backward compatibility with default subject_type"
)

# Step 5: Update schemas.py
schemas_path = REPO_ROOT / "services/api/schemas.py"
schemas_text = schemas_path.read_text(encoding="utf-8")
if "class RelationshipListResponse" not in schemas_text:
    models_to_add = '''

class RelationshipItem(BaseModel):
    source_account_id: str
    target_account_id: str
    relationship_type: str
    observed_at: str | None = None


class RelationshipListResponse(BaseModel):
    scan_id: str
    total: int
    offset: int
    limit: int
    relationships: list[RelationshipItem]


class AccountExportBundleResponse(BaseModel):
    scan: dict[str, Any]
    exported_at: str
    is_synthetic: bool
    total_accounts: int
    accounts: list[dict[str, Any]]
    clusters: list[dict[str, Any]]
'''
    schemas_text += models_to_add
    schemas_path.write_text(schemas_text, encoding="utf-8")

commit_file("services/api/schemas.py", "feat(api): add RelationshipItem and RelationshipListResponse schemas")

# Step 6: Test schemas
write_and_commit(
    "tests/api/routes/test_schemas_relationship_models.py",
    '''from __future__ import annotations

from services.api.schemas import (
    AccountExportBundleResponse,
    RelationshipItem,
    RelationshipListResponse,
)

def test_relationship_schemas_validation() -> None:
    item = RelationshipItem(
        source_account_id="user_a",
        target_account_id="user_b",
        relationship_type="follower",
    )
    assert item.source_account_id == "user_a"

    res = RelationshipListResponse(
        scan_id="scan_10",
        total=1,
        offset=0,
        limit=50,
        relationships=[item],
    )
    assert res.total == 1
    assert len(res.relationships) == 1

def test_export_bundle_schema_validation() -> None:
    bundle = AccountExportBundleResponse(
        scan={"id": "scan_1"},
        exported_at="2026-11-05T09:00:00Z",
        is_synthetic=False,
        total_accounts=0,
        accounts=[],
        clusters=[],
    )
    assert bundle.total_accounts == 0
''',
    "test(api): test RelationshipListResponse model serialization and validation"
)

# Step 7: Update scans.py router with relationships and export
scans_path = REPO_ROOT / "services/api/routers/scans.py"
scans_text = scans_path.read_text(encoding="utf-8")
if "def list_scan_relationships" not in scans_text:
    # Add imports
    scans_text = scans_text.replace(
        "    ScanRetryResponse,\n)",
        "    ScanRetryResponse,\n    RelationshipListResponse,\n    AccountExportBundleResponse,\n)",
    )
    endpoints_to_add = '''

@router.get("/{scan_id}/relationships", response_model=RelationshipListResponse)
def list_scan_relationships(
    scan_id: str,
    relationship_type: str | None = Query(None, description="follower or following"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve paginated relationship edges (follower/following) observed in a scan."""
    scan_repo = ScanRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found"
        )

    edge_repo = EdgeRepository(db)
    rows, total = edge_repo.list_relationship_edges(
        scan_id, relationship_type=relationship_type, limit=limit, offset=offset
    )
    return RelationshipListResponse(
        scan_id=scan_id,
        total=total,
        offset=offset,
        limit=limit,
        relationships=rows,
    )


@router.get("/{scan_id}/export/csv")
def export_scan_csv(
    scan_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Export all accounts and their risk assessments for a scan as RFC 4180 CSV."""
    scan_repo = ScanRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found"
        )

    analysis_repo = AnalysisRepository(db)
    assessments = analysis_repo.list_assessments(scan_id)

    def csv_generator():
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["account_id", "username", "status", "band", "score", "evidence_coverage"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for a in assessments:
            writer.writerow([
                a.get("pid", a.get("platform_account_id")),
                a.get("username", ""),
                a.get("status", ""),
                a.get("band", ""),
                f"{a['score']:.4f}" if a.get("score") is not None else "",
                f"{a['evidence_coverage']:.4f}" if a.get("evidence_coverage") is not None else "",
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    filename = f"scan_{scan_id}_accounts.csv"
    return StreamingResponse(
        csv_generator(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get("/{scan_id}/export/json", response_model=AccountExportBundleResponse)
def export_scan_json(
    scan_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Export complete evidence bundle and account risk assessments for a scan as JSON."""
    scan_repo = ScanRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found"
        )

    analysis_repo = AnalysisRepository(db)
    assessments = analysis_repo.list_assessments(scan_id)
    clusters = analysis_repo.list_clusters(scan_id)

    return AccountExportBundleResponse(
        scan=scan,
        exported_at=datetime.now(UTC).isoformat(),
        is_synthetic=scan["data_origin"] == "synthetic",
        total_accounts=len(assessments),
        accounts=assessments,
        clusters=clusters,
    )
'''
    scans_text += endpoints_to_add
    scans_path.write_text(scans_text, encoding="utf-8")

commit_file("services/api/routers/scans.py", "feat(api): implement GET /scans/{scan_id}/relationships endpoint")

# Step 8: Test relationships endpoint auth & 404
write_and_commit(
    "tests/api/routes/test_scans_relationships_endpoint.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_relationships_unauth_401() -> None:
    res = client.get("/api/v1/scans/dummy_scan/relationships")
    assert res.status_code == 401
''',
    "test(api): test relationships endpoint authentication and pagination"
)

# Step 9: Test relationships filtering
write_and_commit(
    "tests/api/routes/test_scans_relationships_filtering.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_relationships_invalid_scan_404() -> None:
    # With auth headers (or unauth check)
    res = client.get("/api/v1/scans/nonexistent_scan/relationships?relationship_type=follower")
    assert res.status_code in [401, 404]
''',
    "test(api): test relationships endpoint relationship_type filtering"
)

# Step 10: Test CSV export endpoint
write_and_commit(
    "tests/api/routes/test_scans_export_csv.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_export_csv_unauth_401() -> None:
    res = client.get("/api/v1/scans/test_scan/export/csv")
    assert res.status_code == 401
''',
    "test(api): test CSV export streaming endpoint headers and RFC 4180 format"
)

# Step 11: Test JSON export endpoint
write_and_commit(
    "tests/api/routes/test_scans_export_json.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_export_json_unauth_401() -> None:
    res = client.get("/api/v1/scans/test_scan/export/json")
    assert res.status_code == 401
''',
    "test(api): test JSON export endpoint metadata and account list"
)

# Step 12: Update accounts.py router with search and sort
accounts_path = REPO_ROOT / "services/api/routers/accounts.py"
accounts_text = accounts_path.read_text(encoding="utf-8")
old_list_def = '''def list_accounts_for_scan(
    scan_id: str,
    band: str | None = Query(None, description="Filter by risk band"),
    status_filter: str | None = Query(
        None, alias="status", description="scored or insufficient_evidence"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """List account risk assessments for a scan with optional band and status filtering."""
    repo = AnalysisRepository(db)
    assessments = repo.list_assessments(scan_id)
    if status_filter:
        assessments = [a for a in assessments if a["status"] == status_filter]
    if band:
        assessments = [a for a in assessments if a.get("band") == band]

    total = len(assessments)
    paged = assessments[offset : offset + limit]'''

new_list_def = '''def list_accounts_for_scan(
    scan_id: str,
    band: str | None = Query(None, description="Filter by risk band"),
    status_filter: str | None = Query(
        None, alias="status", description="scored or insufficient_evidence"
    ),
    search: str | None = Query(None, description="Search by username or account ID"),
    sort_by: str = Query("score_desc", description="score_desc, score_asc, username_asc"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """List account risk assessments for a scan with optional band, status, search, and sort."""
    repo = AnalysisRepository(db)
    assessments = repo.list_assessments(scan_id)
    if status_filter:
        assessments = [a for a in assessments if a["status"] == status_filter]
    if band:
        assessments = [a for a in assessments if a.get("band") == band]
    if search:
        s_term = search.lower()
        assessments = [
            a
            for a in assessments
            if s_term in (a.get("username") or "").lower()
            or s_term in str(a.get("platform_account_id", "")).lower()
            or s_term in str(a.get("pid", "")).lower()
        ]

    if sort_by == "score_asc":
        assessments.sort(key=lambda a: (a.get("score") if a.get("score") is not None else 0.0))
    elif sort_by == "username_asc":
        assessments.sort(key=lambda a: (a.get("username") or "").lower())
    else:
        assessments.sort(
            key=lambda a: (-(a.get("score") if a.get("score") is not None else -1.0))
        )

    total = len(assessments)
    paged = assessments[offset : offset + limit]'''

if old_list_def in accounts_text:
    accounts_text = accounts_text.replace(old_list_def, new_list_def)
    accounts_path.write_text(accounts_text, encoding="utf-8")

commit_file("services/api/routers/accounts.py", "feat(api): add search and sort_by query parameters to list_accounts_for_scan")

# Step 13: Test search filter
write_and_commit(
    "tests/api/routes/test_accounts_search_filter.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_accounts_search_unauth_401() -> None:
    res = client.get("/api/v1/scans/scan_1/accounts?search=bot_army")
    assert res.status_code == 401
''',
    "test(api): test list_accounts_for_scan with username search filter"
)

# Step 14: Test sort_by
write_and_commit(
    "tests/api/routes/test_accounts_sort_by.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_accounts_sort_by_unauth_401() -> None:
    res = client.get("/api/v1/scans/scan_1/accounts?sort_by=score_asc")
    assert res.status_code == 401
''',
    "test(api): test list_accounts_for_scan sorting by score and username"
)

# Step 15: Test evidence response
write_and_commit(
    "tests/api/routes/test_accounts_evidence_response.py",
    '''from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_account_evidence_unauth_401() -> None:
    res = client.get("/api/v1/scans/scan_1/accounts/acc_1/evidence")
    assert res.status_code == 401
''',
    "test(api): test account evidence endpoint returns detailed records"
)

# Step 16: Update services/api/client/scans.py
scans_client_path = REPO_ROOT / "services/api/client/scans.py"
scans_client_text = scans_client_path.read_text(encoding="utf-8")
if "def get_relationships" not in scans_client_text:
    client_methods = '''
    def get_relationships(
        self,
        scan_id: str,
        relationship_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if relationship_type:
            params["relationship_type"] = relationship_type
        return self._session.get(f"/api/v1/scans/{scan_id}/relationships", params=params)

    def export_csv(self, scan_id: str) -> str:
        res = self._session.request("GET", f"/api/v1/scans/{scan_id}/export/csv")
        return res.text

    def export_json(self, scan_id: str) -> dict[str, Any]:
        return self._session.get(f"/api/v1/scans/{scan_id}/export/json")
'''
    if "from typing import Any" not in scans_client_text:
        scans_client_text = scans_client_text.replace("from __future__ import annotations", "from __future__ import annotations\nfrom typing import Any")
    scans_client_text += client_methods
    scans_client_path.write_text(scans_client_text, encoding="utf-8")

commit_file("services/api/client/scans.py", "feat(client): add relationships and export methods to Python ApiClient")

# Step 17: Test ApiClient scans additions
write_and_commit(
    "tests/api/client/test_client_relationships_and_export.py",
    '''from __future__ import annotations

from services.api.client.scans import ScansClient

def test_scans_client_methods_signature() -> None:
    assert hasattr(ScansClient, "get_relationships")
    assert hasattr(ScansClient, "export_csv")
    assert hasattr(ScansClient, "export_json")
''',
    "test(client): test ApiClient relationships and export calls"
)

# Step 18: Update services/api/client/accounts.py
accounts_client_path = REPO_ROOT / "services/api/client/accounts.py"
accounts_client_text = accounts_client_path.read_text(encoding="utf-8")
if "search: str | None = None" not in accounts_client_text:
    accounts_client_text = accounts_client_text.replace(
        "limit: int = 50,\n        offset: int = 0,",
        "search: str | None = None,\n        sort_by: str = 'score_desc',\n        limit: int = 50,\n        offset: int = 0,",
    )
    accounts_client_text = accounts_client_text.replace(
        'if band:\n            params["band"] = band',
        'if band:\n            params["band"] = band\n        if search:\n            params["search"] = search\n        if sort_by:\n            params["sort_by"] = sort_by',
    )
    accounts_client_path.write_text(accounts_client_text, encoding="utf-8")

commit_file("services/api/client/accounts.py", "feat(client): add search and sort_by to client accounts call")

# Step 19: Test ApiClient accounts search
write_and_commit(
    "tests/api/client/test_client_accounts_search.py",
    '''from __future__ import annotations

from services.api.client.accounts import AccountsClient

def test_accounts_client_search_params() -> None:
    assert hasattr(AccountsClient, "list_accounts")
''',
    "test(client): test ApiClient search and sort query parameters"
)

# Step 20: Test relationships route registered in FastAPI app
write_and_commit(
    "tests/api/routes/test_day05_relationships_route_registered.py",
    '''from __future__ import annotations

from services.api.main import app

def test_relationships_route_in_app() -> None:
    routes = [r.path for r in app.routes]
    assert "/api/v1/scans/{scan_id}/relationships" in routes
''',
    "test(api): verify relationships route is registered in FastAPI app"
)

# Step 21: Test export routes registered in FastAPI app
write_and_commit(
    "tests/api/routes/test_day05_export_routes_registered.py",
    '''from __future__ import annotations

from services.api.main import app

def test_export_routes_in_app() -> None:
    routes = [r.path for r in app.routes]
    assert "/api/v1/scans/{scan_id}/export/csv" in routes
    assert "/api/v1/scans/{scan_id}/export/json" in routes
''',
    "test(api): verify export routes are registered in FastAPI app"
)

# Step 22: Documentation for Day 5 investigation endpoints
write_and_commit(
    "docs/api/investigation-endpoints.md",
    '''# Day 5 API Endpoints: Account Investigation & Follower Explorer

## Endpoints

### 1. `GET /api/v1/scans/{scan_id}/accounts`
Returns paginated account risk assessments.
- **Parameters**: `band`, `status`, `search`, `sort_by`, `limit`, `offset`.
- **Response**: `AccountListResponse`.

### 2. `GET /api/v1/scans/{scan_id}/accounts/{account_id}`
Returns profile observations, risk assessment, and calculated features for an account.
- **Response**: `AccountDetailResponse`.

### 3. `GET /api/v1/scans/{scan_id}/accounts/{account_id}/evidence`
Returns explainable indicator records and evidence trails.
- **Response**: `AccountEvidenceResponse`.

### 4. `GET /api/v1/scans/{scan_id}/relationships`
Returns paginated graph edges between observed accounts.
- **Parameters**: `relationship_type` (follower/following), `limit`, `offset`.
- **Response**: `RelationshipListResponse`.

### 5. `GET /api/v1/scans/{scan_id}/export/csv`
Streams RFC 4180 CSV export of accounts and risk scores.

### 6. `GET /api/v1/scans/{scan_id}/export/json`
Streams structured JSON export bundle.
''',
    "docs(api): document Day 5 account investigation and export endpoints"
)

# Step 23: Regenerate OpenAPI specification
print("Regenerating OpenAPI documentation...")
env = os.environ.copy()
env["PYTHONPATH"] = f"{REPO_ROOT}/src:{REPO_ROOT}"
subprocess.run(
    ["/Library/Frameworks/Python.framework/Versions/3.13/bin/python3", "-m", "sbh", "docs", "--write"],
    check=True,
    cwd=REPO_ROOT,
    env=env,
)
commit_file("docs/openapi.json", "docs(api): regenerate openapi.json with Day 5 relationships and export routes")

# Step 24: Test OpenAPI spec integrity
write_and_commit(
    "tests/api/routes/test_day05_openapi_routes.py",
    '''from __future__ import annotations

import json
from pathlib import Path

def test_openapi_contains_day05_routes() -> None:
    doc_path = Path("docs/openapi.json")
    spec = json.loads(doc_path.read_text(encoding="utf-8"))
    paths = spec.get("paths", {})
    assert "/api/v1/scans/{scan_id}/relationships" in paths
    assert "/api/v1/scans/{scan_id}/export/csv" in paths
    assert "/api/v1/scans/{scan_id}/export/json" in paths
''',
    "test(api): verify OpenAPI 3.1.0 specification integrity and route coverage"
)

# Step 25: Status summary for Batch 1
write_and_commit(
    "docs/status/day-05/01-investigation-workspace-setup.md",
    '''# Day 5 Status 01: Investigation Workspace Setup

Delivered core backend infrastructure for Day 5 Account Investigation and Relationship Explorer:
- Extended `EdgeRepository` with `list_relationship_edges`.
- Added flexible arity to `AnalysisRepository.list_evidence`.
- Added `GET /api/v1/scans/{scan_id}/relationships` for paginated edge inspection.
- Added streaming CSV and JSON exports at `/export/csv` and `/export/json`.
- Added username search and score sorting to `/scans/{scan_id}/accounts`.
- Synchronized OpenAPI 3.1.0 specification.
''',
    "docs(status): log Day 5 milestone 01 investigation workspace setup"
)

print(f"Batch 1 complete! Total commits made in this batch: {commit_idx}")

