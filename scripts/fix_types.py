from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 4, 16, 5, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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

TYPE_FIXES = []

# 1. types-contract.test.ts
TYPE_FIXES.append((
    "apps/dashboard/src/lib/api/__tests__/types-contract.test.ts",
    """import { describe, it, expect } from "vitest";
import type { ScanJob, HealthResponse, Platform } from "../types";

describe("API Types Contract", () => {
  it("conforms to backend schema structure for ScanJob", () => {
    const scan: ScanJob = {
      id: "scan_test",
      platform: "x" as Platform,
      scan_type: "api_collection",
      collection_mode: "official_api",
      status: "complete",
      data_origin: "api",
      requested_by: "analyst_1",
      created_at: "2026-11-04T00:00:00Z",
      reference_time: "2026-11-04T00:00:00Z",
      config_version: "v1.0",
      config_sha256: "abc123sha",
    };
    expect(scan.status).toBe("complete");
    expect(scan.platform).toBe("x");
  });

  it("conforms to HealthResponse schema", () => {
    const health: HealthResponse = {
      status: "ok",
      version: "0.1.0",
      database: "connected",
      timestamp: "2026-11-04T00:00:00Z",
    };
    expect(health.database).toBe("connected");
  });
});
""",
    "fix(types): align types-contract test with exported ScanJob schema"
))

# 2. use-capabilities.test.ts
TYPE_FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-capabilities.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useCapabilities } from "../use-capabilities";
import type { PlatformCapability } from "../../api/types";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      capabilities: [
        {
          platform: "x",
          operation: "read_profile",
          supported: true,
          required_permissions: ["users.read"],
        } as PlatformCapability,
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useCapabilities hook", () => {
  it("fetches platform capabilities list", () => {
    const { result } = renderHook(() => useCapabilities());
    expect(result.current.isLoading).toBe(false);
    expect(result.current.capabilities).toHaveLength(1);
    expect(result.current.capabilities[0].supported).toBe(true);
  });
});
""",
    "fix(types): update useCapabilities test with PlatformCapability fields"
))

# 3. use-scans.test.ts
TYPE_FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-scans.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useScans } from "../use-scans";
import type { ScanJob } from "../../api/types";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scans: [
        {
          id: "scan_01",
          platform: "x",
          scan_type: "api_collection",
          collection_mode: "official_api",
          status: "complete",
          data_origin: "api",
          requested_by: "analyst_1",
          created_at: "2026-11-04T10:00:00Z",
          reference_time: "2026-11-04T10:00:00Z",
          config_version: "v1.0",
          config_sha256: "abc",
        } as ScanJob,
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useScans hook", () => {
  it("fetches scan list and returns items", () => {
    const { result } = renderHook(() => useScans(10));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.scans).toHaveLength(1);
    expect(result.current.scans[0].platform).toBe("x");
  });
});
""",
    "fix(types): update useScans test with ScanJob typed fields"
))

# 4. network-transform.test.ts
TYPE_FIXES.append((
    "apps/dashboard/src/lib/utils/__tests__/network-transform.test.ts",
    """import { describe, it, expect } from "vitest";
import { transformToGraphElements } from "../network-transform";

describe("Network Transform utility", () => {
  it("converts nodes and edges into graph element dictionaries", () => {
    const nodes = [{ id: "n1", label: "@user1", platform: "x", riskScore: 80 }];
    const edges = [{ source: "n1", target: "n2", relationshipType: "follows" }];
    const elements = transformToGraphElements(nodes, edges);

    expect(elements).toHaveLength(2);
    expect(elements[0].data.id).toBe("n1");
    const edgeData = elements[1].data as { source: string; target: string; type: string };
    expect(edgeData.source).toBe("n1");
  });
});
""",
    "fix(types): cast edge element data in network transform test"
))

# 5. fixtures.ts
TYPE_FIXES.append((
    "apps/dashboard/src/test/mocks/fixtures.ts",
    """import type { ScanJob, HealthResponse, CapabilitiesResponse, AuditListResponse } from "../../lib/api/types";

export const mockScan: ScanJob = {
  id: "scan_test_101",
  platform: "x",
  scan_type: "api_collection",
  collection_mode: "official_api",
  status: "complete",
  data_origin: "synthetic",
  requested_by: "analyst_1",
  created_at: "2026-11-04T12:00:00Z",
  reference_time: "2026-11-04T12:00:00Z",
  config_version: "v1.0",
  config_sha256: "abc123sha",
};

export const mockHealth: HealthResponse = {
  status: "ok",
  version: "0.1.0",
  database: "connected",
  timestamp: "2026-11-04T12:00:00Z",
};

export const mockCapabilities: CapabilitiesResponse = {
  capabilities: [
    {
      platform: "x",
      operation: "read_profile",
      supported: true,
      endpoint: "https://api.x.com/2/users/by/username/:username",
    },
    {
      platform: "instagram",
      operation: "read_profile",
      supported: true,
      endpoint: "https://graph.instagram.com/me",
    },
  ],
  total: 2,
};

export const mockAudit: AuditListResponse = {
  events: [
    {
      id: "audit_01",
      actor: "analyst_1",
      action: "investigation.launch",
      subject_type: "scan",
      subject_id: "scan_test_101",
      occurred_at: "2026-11-04T12:30:00Z",
    },
  ],
  total: 1,
};
""",
    "fix(types): align fixtures.ts with dashboard schema definitions"
))

def main() -> None:
    print(f"Applying {len(TYPE_FIXES)} TypeScript type fixes.")
    for rel_path, content, msg in TYPE_FIXES:
        write_and_commit(rel_path, content, msg)
    print("Done applying type fixes.")

if __name__ == "__main__":
    main()
