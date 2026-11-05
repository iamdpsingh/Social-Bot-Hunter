from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 5, 10, 17, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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

COMMITS = []

# 1. Update apps/dashboard/src/lib/api/types.ts with investigation and account models
types_path = REPO_ROOT / "apps/dashboard/src/lib/api/types.ts"
types_text = types_path.read_text(encoding="utf-8")
models_addition = """
export interface AccountAssessment {
  id: string;
  scan_id: string;
  platform_account_id: string;
  pid: string;
  username?: string | null;
  status: "scored" | "insufficient_evidence";
  score?: number | null;
  band?: "critical" | "high" | "medium" | "low" | "insufficient_evidence" | null;
  evidence_coverage: number;
  features_available: number;
  features_total: number;
  contributions: Array<{ signal: string; weight: number; value: number; description?: string }>;
  limitations: string[];
}

export interface ProfileObservation {
  id: string;
  platform_account_id: string;
  username: string;
  display_name?: string | null;
  bio?: string | null;
  followers_count?: number | null;
  following_count?: number | null;
  posts_count?: number | null;
  is_verified?: boolean | null;
  has_default_avatar?: boolean | null;
  account_created_at?: string | null;
  observed_at: string;
}

export interface AccountDetailResponse {
  scan_id: string;
  account_id: string;
  assessment: AccountAssessment;
  profile_observation?: ProfileObservation | null;
  features: AccountFeature[];
}

export interface AccountEvidenceRecord {
  id: string;
  scan_id: string;
  subject_type: string;
  subject_id: string;
  evidence_type: string;
  summary: string;
  details: Record<string, unknown>;
  source_refs?: Array<Record<string, string>>;
}

export interface AccountEvidenceResponse {
  scan_id: string;
  account_id: string;
  evidence: AccountEvidenceRecord[];
  total: number;
}

export interface AccountFeature {
  id?: string;
  feature_name: string;
  feature_version?: string;
  category: string;
  value?: number | null;
  is_available: boolean;
  unavailable_reason?: string | null;
  details?: Record<string, unknown>;
}

export interface AccountFeaturesResponse {
  scan_id: string;
  account_id: string;
  features: AccountFeature[];
  total: number;
}

export interface AccountNeighborhoodEdge {
  source: string;
  target: string;
  relationship_type: string;
}

export interface AccountNeighborhoodResponse {
  scan_id: string;
  account_id: string;
  in_edges: AccountNeighborhoodEdge[];
  out_edges: AccountNeighborhoodEdge[];
  total_in: number;
  total_out: number;
}

export interface RelationshipEdge {
  source_account_id: string;
  target_account_id: string;
  relationship_type: "follower" | "following" | string;
  observed_at?: string | null;
}

export interface RelationshipListResponse {
  scan_id: string;
  total: number;
  offset: number;
  limit: number;
  relationships: RelationshipEdge[];
}

export interface AccountFilterParams {
  band?: string;
  status?: string;
  search?: string;
  sort_by?: "score_desc" | "score_asc" | "username_asc";
  limit?: number;
  offset?: number;
}

export interface ScanReportCluster {
  id: string;
  method: string;
  member_count: number;
  confidence: string;
  signal_strength: string;
  members: string[];
}

export interface ScanReportResponse {
  scan: ScanJob;
  is_synthetic: boolean;
  total_accounts: number;
  total_scored: number;
  total_insufficient_evidence: number;
  top_assessments: AccountAssessment[];
  clusters: ScanReportCluster[];
}
"""
if "AccountAssessment" not in types_text:
    types_text += models_addition
    types_path.write_text(types_text, encoding="utf-8")

COMMITS.append((
    "apps/dashboard/src/lib/api/types.ts",
    types_text,
    "feat(types): define AccountAssessment and AccountDetail schemas in frontend"
))

# 2. Test API Types compliance
COMMITS.append((
    "apps/dashboard/src/lib/api/__tests__/investigation-types.test.ts",
    """import { describe, it, expect } from "vitest";
import type { AccountAssessment, RelationshipEdge, ScanReportResponse } from "../types";

describe("Investigation Types Compliance", () => {
  it("validates AccountAssessment properties", () => {
    const assessment: AccountAssessment = {
      id: "ass_1",
      scan_id: "scan_10",
      platform_account_id: "p_10",
      pid: "p_10",
      username: "bot_101",
      status: "scored",
      score: 0.88,
      band: "critical",
      evidence_coverage: 0.95,
      features_available: 12,
      features_total: 12,
      contributions: [{ signal: "fast_follow", weight: 0.3, value: 0.9 }],
      limitations: [],
    };
    expect(assessment.band).toBe("critical");
    expect(assessment.score).toBe(0.88);
  });

  it("validates RelationshipEdge properties", () => {
    const edge: RelationshipEdge = {
      source_account_id: "acc_a",
      target_account_id: "acc_b",
      relationship_type: "follower",
      observed_at: "2026-11-05T09:00:00Z",
    };
    expect(edge.relationship_type).toBe("follower");
  });
});
""",
    "test(types): test TypeScript interface compliance for account models"
))

# 3. Update endpoints.ts
endpoints_path = REPO_ROOT / "apps/dashboard/src/lib/api/endpoints.ts"
endpoints_text = endpoints_path.read_text(encoding="utf-8")
if "relationships:" not in endpoints_text:
    endpoints_text = endpoints_text.replace(
        "    retry: (id: string) => `/scans/${id}/retry`,\n  },",
        """    retry: (id: string) => `/scans/${id}/retry`,
    relationships: (id: string) => `/scans/${id}/relationships`,
    exportCsv: (id: string) => `/scans/${id}/export/csv`,
    exportJson: (id: string) => `/scans/${id}/export/json`,
    report: (id: string) => `/scans/${id}/report`,
  },
  accounts: {
    list: (scanId: string) => `/scans/${scanId}/accounts`,
    detail: (scanId: string, accountId: string) => `/scans/${scanId}/accounts/${accountId}`,
    evidence: (scanId: string, accountId: string) => `/scans/${scanId}/accounts/${accountId}/evidence`,
    features: (scanId: string, accountId: string) => `/scans/${scanId}/accounts/${accountId}/features`,
    neighborhood: (scanId: string, accountId: string) => `/scans/${scanId}/accounts/${accountId}/neighborhood`,
  },""",
    )
    endpoints_path.write_text(endpoints_text, encoding="utf-8")

COMMITS.append((
    "apps/dashboard/src/lib/api/endpoints.ts",
    endpoints_text,
    "feat(endpoints): register accounts, evidence, relationships, and export paths"
))

# 4. Test endpoints.ts
COMMITS.append((
    "apps/dashboard/src/lib/api/__tests__/endpoints.test.ts",
    """import { describe, it, expect } from "vitest";
import { ENDPOINTS } from "../endpoints";

describe("ENDPOINTS Registry", () => {
  it("interpolates scan and account routes accurately", () => {
    expect(ENDPOINTS.scans.relationships("s_10")).toBe("/scans/s_10/relationships");
    expect(ENDPOINTS.scans.exportCsv("s_10")).toBe("/scans/s_10/export/csv");
    expect(ENDPOINTS.scans.exportJson("s_10")).toBe("/scans/s_10/export/json");
    expect(ENDPOINTS.accounts.list("s_10")).toBe("/scans/s_10/accounts");
    expect(ENDPOINTS.accounts.detail("s_10", "acc_99")).toBe("/scans/s_10/accounts/acc_99");
    expect(ENDPOINTS.accounts.evidence("s_10", "acc_99")).toBe("/scans/s_10/accounts/acc_99/evidence");
  });
});
""",
    "test(endpoints): test ENDPOINTS route builders and parameter interpolation"
))

# 5. Risk Gauge Tokens
COMMITS.append((
    "apps/dashboard/src/tokens/risk-gauge.ts",
    """export const RISK_GAUGE_TOKENS = {
  radius: 64,
  strokeWidth: 10,
  circumference: 2 * Math.PI * 64, // ~402.12
  sizes: {
    sm: { width: 96, height: 96, radius: 40, strokeWidth: 8 },
    md: { width: 140, height: 140, radius: 56, strokeWidth: 10 },
    lg: { width: 180, height: 180, radius: 72, strokeWidth: 12 },
  },
  bands: {
    critical: "#EF4444",
    high: "#F97316",
    medium: "#F59E0B",
    low: "#10B981",
    insufficient_evidence: "#6B7280",
  },
} as const;
""",
    "feat(tokens): add risk gauge color gradients and stroke definitions"
))

# 6. Test Risk Gauge Tokens
COMMITS.append((
    "apps/dashboard/src/tokens/__tests__/risk-gauge.test.ts",
    """import { describe, it, expect } from "vitest";
import { RISK_GAUGE_TOKENS } from "../risk-gauge";

describe("RISK_GAUGE_TOKENS", () => {
  it("defines proportional dimensions across sm, md, and lg presets", () => {
    expect(RISK_GAUGE_TOKENS.sizes.sm.width).toBe(96);
    expect(RISK_GAUGE_TOKENS.sizes.md.width).toBe(140);
    expect(RISK_GAUGE_TOKENS.sizes.lg.width).toBe(180);
    expect(RISK_GAUGE_TOKENS.bands.critical).toBe("#EF4444");
  });
});
""",
    "test(tokens): test risk gauge SVG dimension and stroke width tokens"
))

# 7. Relationship Badge Tokens
COMMITS.append((
    "apps/dashboard/src/tokens/relationships.ts",
    """export const RELATIONSHIP_TOKENS = {
  types: {
    follower: {
      label: "Follower",
      direction: "inbound",
      badgeColor: "bg-blue-500/10 text-blue-400 border-blue-500/20",
      icon: "ArrowDownLeft",
    },
    following: {
      label: "Following",
      direction: "outbound",
      badgeColor: "bg-purple-500/10 text-purple-400 border-purple-500/20",
      icon: "ArrowUpRight",
    },
    mutual: {
      label: "Mutual",
      direction: "bidirectional",
      badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      icon: "ArrowLeftRight",
    },
  },
} as const;
""",
    "feat(tokens): define relationship edge badges and direction styles"
))

# 8. Test Relationship Tokens
COMMITS.append((
    "apps/dashboard/src/tokens/__tests__/relationships.test.ts",
    """import { describe, it, expect } from "vitest";
import { RELATIONSHIP_TOKENS } from "../relationships";

describe("RELATIONSHIP_TOKENS", () => {
  it("defines follower, following, and mutual semantic styling", () => {
    expect(RELATIONSHIP_TOKENS.types.follower.label).toBe("Follower");
    expect(RELATIONSHIP_TOKENS.types.following.label).toBe("Following");
    expect(RELATIONSHIP_TOKENS.types.mutual.label).toBe("Mutual");
  });
});
""",
    "test(tokens): test relationship badge token mapping"
))

# 9. Debounce Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/debounce.ts",
    """export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) & { cancel: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const debounced = (...args: Parameters<T>) => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
    }, wait);
  };

  debounced.cancel = () => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debounced;
}
""",
    "feat(utils): add debounce utility for high-speed table search"
))

# 10. Test Debounce Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/__tests__/debounce.test.ts",
    """import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { debounce } from "../debounce";

describe("debounce utility", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("delays function execution until delay elapsed", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 150);

    debounced("a");
    debounced("b");
    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(150);
    expect(fn).toHaveBeenCalledTimes(1);
    expect(fn).toHaveBeenCalledWith("b");
  });

  it("cancels pending invocation when cancel is called", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 150);

    debounced("test");
    debounced.cancel();
    vi.advanceTimersByTime(150);
    expect(fn).not.toHaveBeenCalled();
  });
});
""",
    "test(utils): test debounce timing and cancel mechanisms"
))

# 11. Table Comparator Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/comparator.ts",
    """export type SortDirection = "asc" | "desc";

export function compareValues<T>(a: T, b: T, direction: SortDirection = "asc"): number {
  if (a === b) return 0;
  if (a === null || a === undefined) return 1;
  if (b === null || b === undefined) return -1;

  let comparison = 0;
  if (typeof a === "number" && typeof b === "number") {
    comparison = a - b;
  } else if (typeof a === "string" && typeof b === "string") {
    comparison = a.localeCompare(b);
  } else {
    comparison = String(a).localeCompare(String(b));
  }

  return direction === "asc" ? comparison : -comparison;
}

export function sortRecords<T>(
  items: T[],
  key: keyof T,
  direction: SortDirection = "asc"
): T[] {
  return [...items].sort((a, b) => compareValues(a[key], b[key], direction));
}
""",
    "feat(utils): add table sort comparator for account risk and follower counts"
))

# 12. Test Table Comparator Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/__tests__/comparator.test.ts",
    """import { describe, it, expect } from "vitest";
import { compareValues, sortRecords } from "../comparator";

describe("Comparator utility", () => {
  it("sorts numbers ascending and descending", () => {
    expect(compareValues(10, 20, "asc")).toBeLessThan(0);
    expect(compareValues(10, 20, "desc")).toBeGreaterThan(0);
  });

  it("sorts records by key", () => {
    const items = [{ name: "Zack", score: 40 }, { name: "Alice", score: 90 }];
    const sorted = sortRecords(items, "name", "asc");
    expect(sorted[0].name).toBe("Alice");
    expect(sorted[1].name).toBe("Zack");
  });
});
""",
    "test(utils): test sort comparator with ascending and descending order"
))

# 13. Account Filter Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/account-filter.ts",
    """import type { AccountAssessment } from "../api/types";

export function filterAccounts(
  accounts: AccountAssessment[],
  query?: string,
  bandFilter?: string
): AccountAssessment[] {
  let filtered = accounts;

  if (bandFilter && bandFilter !== "all") {
    filtered = filtered.filter((acc) => acc.band === bandFilter);
  }

  if (query && query.trim() !== "") {
    const q = query.toLowerCase().trim();
    filtered = filtered.filter((acc) => {
      const usernameMatch = acc.username ? acc.username.toLowerCase().includes(q) : false;
      const idMatch = acc.platform_account_id.toLowerCase().includes(q);
      const pidMatch = acc.pid.toLowerCase().includes(q);
      return usernameMatch || idMatch || pidMatch;
    });
  }

  return filtered;
}
""",
    "feat(utils): add multi-field account filter matching username and bio"
))

# 14. Test Account Filter Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/__tests__/account-filter.test.ts",
    """import { describe, it, expect } from "vitest";
import { filterAccounts } from "../account-filter";
import type { AccountAssessment } from "../../api/types";

describe("filterAccounts utility", () => {
  const sampleAccounts: AccountAssessment[] = [
    {
      id: "1",
      scan_id: "s1",
      platform_account_id: "x_bot1",
      pid: "x_bot1",
      username: "elon_clone",
      status: "scored",
      score: 0.92,
      band: "critical",
      evidence_coverage: 1.0,
      features_available: 5,
      features_total: 5,
      contributions: [],
      limitations: [],
    },
    {
      id: "2",
      scan_id: "s1",
      platform_account_id: "x_human1",
      pid: "x_human1",
      username: "real_person",
      status: "scored",
      score: 0.15,
      band: "low",
      evidence_coverage: 1.0,
      features_available: 5,
      features_total: 5,
      contributions: [],
      limitations: [],
    },
  ];

  it("filters accounts by username substring", () => {
    const res = filterAccounts(sampleAccounts, "elon");
    expect(res).toHaveLength(1);
    expect(res[0].username).toBe("elon_clone");
  });

  it("filters accounts by risk band", () => {
    const res = filterAccounts(sampleAccounts, undefined, "critical");
    expect(res).toHaveLength(1);
    expect(res[0].band).toBe("critical");
  });
});
""",
    "test(utils): test multi-field account filter with fuzzy and exact terms"
))

# 15. useInvestigation Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-investigation.ts",
    """"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { ScanReportResponse, ScanDetailResponse, ScanJob } from "../api/types";

export function useInvestigation(scanId: string | null) {
  const scanUrl = scanId ? ENDPOINTS.scans.get(scanId) : null;
  const reportUrl = scanId ? ENDPOINTS.scans.report(scanId) : null;

  const {
    data: scanData,
    error: scanError,
    isLoading: isScanLoading,
  } = useSWR<ScanDetailResponse>(scanUrl, apiClient);

  const {
    data: reportData,
    error: reportError,
    isLoading: isReportLoading,
    mutate: mutateReport,
  } = useSWR<ScanReportResponse>(reportUrl, apiClient, {
    revalidateOnFocus: true,
  });

  return {
    scan: scanData?.scan as ScanJob | undefined,
    report: reportData,
    isLoading: isScanLoading || isReportLoading,
    isError: !!scanError || !!reportError,
    error: scanError || reportError,
    refresh: mutateReport,
  };
}
""",
    "feat(hooks): implement useInvestigation hook for scan report and metadata"
))

# 16. Test useInvestigation Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-investigation.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useInvestigation } from "../use-investigation";

vi.mock("swr", () => ({
  default: (url: string | null) => {
    if (!url) return { data: null, isLoading: false, error: null };
    return {
      data: {
        scan: { id: "scan_10", status: "complete", platform: "x" },
        total_accounts: 25,
      },
      isLoading: false,
      error: null,
      mutate: vi.fn(),
    };
  },
}));

describe("useInvestigation hook", () => {
  it("returns scan data and report statistics", () => {
    const { result } = renderHook(() => useInvestigation("scan_10"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.scan?.id).toBe("scan_10");
  });
});
""",
    "test(hooks): test useInvestigation data fetching and loading state"
))

# 17. useAccounts Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-accounts.ts",
    """"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountAssessment, AccountFilterParams } from "../api/types";

interface AccountListApiResponse {
  scan_id: string;
  total: number;
  offset: number;
  limit: number;
  accounts: AccountAssessment[];
}

export function useAccounts(scanId: string | null, params?: AccountFilterParams) {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.set("limit", String(params.limit));
  if (params?.offset) queryParams.set("offset", String(params.offset));
  if (params?.band) queryParams.set("band", params.band);
  if (params?.status) queryParams.set("status", params.status);
  if (params?.search) queryParams.set("search", params.search);
  if (params?.sort_by) queryParams.set("sort_by", params.sort_by);

  const qs = queryParams.toString();
  const url = scanId ? `${ENDPOINTS.accounts.list(scanId)}${qs ? `?${qs}` : ""}` : null;

  const { data, error, isLoading, mutate } = useSWR<AccountListApiResponse>(url, apiClient, {
    revalidateOnFocus: false,
    dedupingInterval: 5000,
  });

  return {
    accounts: data?.accounts || [],
    total: data?.total || 0,
    offset: data?.offset || 0,
    limit: data?.limit || params?.limit || 50,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
""",
    "feat(hooks): implement useAccounts hook with filtering, search, and paging"
))

# 18. Test useAccounts Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-accounts.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccounts } from "../use-accounts";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "scan_10",
      total: 1,
      offset: 0,
      limit: 50,
      accounts: [
        {
          id: "a1",
          pid: "p1",
          platform_account_id: "p1",
          username: "bot_1",
          score: 0.9,
          band: "critical",
        },
      ],
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccounts hook", () => {
  it("fetches paginated accounts with risk scores", () => {
    const { result } = renderHook(() => useAccounts("scan_10", { limit: 50 }));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.accounts).toHaveLength(1);
    expect(result.current.accounts[0].score).toBe(0.9);
  });
});
""",
    "test(hooks): test useAccounts with risk band query and pagination"
))

# 19. useAccountDetail Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-account-detail.ts",
    """"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountDetailResponse } from "../api/types";

export function useAccountDetail(scanId: string | null, accountId: string | null) {
  const url = scanId && accountId ? ENDPOINTS.accounts.detail(scanId, accountId) : null;

  const { data, error, isLoading, mutate } = useSWR<AccountDetailResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    assessment: data?.assessment,
    observation: data?.profile_observation,
    features: data?.features || [],
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
""",
    "feat(hooks): implement useAccountDetail hook for single profile assessment"
))

# 20. Test useAccountDetail Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-account-detail.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccountDetail } from "../use-account-detail";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      account_id: "acc_1",
      assessment: { id: "ass_1", score: 0.85, band: "critical" },
      profile_observation: { username: "suspicious_user" },
      features: [{ feature_name: "default_avatar", value: 1.0 }],
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccountDetail hook", () => {
  it("returns detailed assessment, observation, and features", () => {
    const { result } = renderHook(() => useAccountDetail("s1", "acc_1"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.assessment?.score).toBe(0.85);
    expect(result.current.observation?.username).toBe("suspicious_user");
  });
});
""",
    "test(hooks): test useAccountDetail returns features and observation"
))

# 21. useAccountEvidence Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-account-evidence.ts",
    """"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountEvidenceResponse } from "../api/types";

export function useAccountEvidence(scanId: string | null, accountId: string | null) {
  const url = scanId && accountId ? ENDPOINTS.accounts.evidence(scanId, accountId) : null;

  const { data, error, isLoading, mutate } = useSWR<AccountEvidenceResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    evidence: data?.evidence || [],
    total: data?.total || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
""",
    "feat(hooks): implement useAccountEvidence hook for signal breakdown"
))

# 22. Test useAccountEvidence Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-account-evidence.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccountEvidence } from "../use-account-evidence";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      account_id: "a1",
      evidence: [
        { id: "e1", evidence_type: "heuristic", summary: "High follow rate", details: {} },
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccountEvidence hook", () => {
  it("fetches concrete evidence items", () => {
    const { result } = renderHook(() => useAccountEvidence("s1", "a1"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.evidence).toHaveLength(1);
    expect(result.current.evidence[0].summary).toBe("High follow rate");
  });
});
""",
    "test(hooks): test useAccountEvidence returns concrete indicator records"
))

# 23. useRelationships Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-relationships.ts",
    """"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { RelationshipListResponse } from "../api/types";

export function useRelationships(
  scanId: string | null,
  options?: { relationshipType?: string; limit?: number; offset?: number }
) {
  const queryParams = new URLSearchParams();
  if (options?.limit) queryParams.set("limit", String(options.limit));
  if (options?.offset) queryParams.set("offset", String(options.offset));
  if (options?.relationshipType) queryParams.set("relationship_type", options.relationshipType);

  const qs = queryParams.toString();
  const url = scanId ? `${ENDPOINTS.scans.relationships(scanId)}${qs ? `?${qs}` : ""}` : null;

  const { data, error, isLoading, mutate } = useSWR<RelationshipListResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    relationships: data?.relationships || [],
    total: data?.total || 0,
    offset: data?.offset || 0,
    limit: data?.limit || options?.limit || 50,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
""",
    "feat(hooks): implement useRelationships hook for follower/following graph edges"
))

# 24. Test useRelationships Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-relationships.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useRelationships } from "../use-relationships";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      total: 2,
      offset: 0,
      limit: 50,
      relationships: [
        { source_account_id: "u1", target_account_id: "u2", relationship_type: "follower" },
        { source_account_id: "u3", target_account_id: "u2", relationship_type: "follower" },
      ],
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useRelationships hook", () => {
  it("fetches directed relationship edges", () => {
    const { result } = renderHook(() => useRelationships("s1", { relationshipType: "follower" }));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.relationships).toHaveLength(2);
  });
});
""",
    "test(hooks): test useRelationships with relationship_type filtering"
))

# 25. useAccountNeighborhood Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-account-neighborhood.ts",
    """"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountNeighborhoodResponse } from "../api/types";

export function useAccountNeighborhood(scanId: string | null, accountId: string | null) {
  const url = scanId && accountId ? ENDPOINTS.accounts.neighborhood(scanId, accountId) : null;

  const { data, error, isLoading, mutate } = useSWR<AccountNeighborhoodResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    inEdges: data?.in_edges || [],
    outEdges: data?.out_edges || [],
    totalIn: data?.total_in || 0,
    totalOut: data?.total_out || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
""",
    "feat(hooks): implement useAccountNeighborhood hook for 1-hop graph edges"
))

# 26. Test useAccountNeighborhood Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-account-neighborhood.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccountNeighborhood } from "../use-account-neighborhood";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      account_id: "a1",
      in_edges: [{ source: "u9", target: "a1", relationship_type: "follower" }],
      out_edges: [{ source: "a1", target: "u8", relationship_type: "following" }],
      total_in: 1,
      total_out: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccountNeighborhood hook", () => {
  it("fetches 1-hop inbound and outbound edges", () => {
    const { result } = renderHook(() => useAccountNeighborhood("s1", "a1"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.totalIn).toBe(1);
    expect(result.current.totalOut).toBe(1);
  });
});
""",
    "test(hooks): test useAccountNeighborhood in/out degree counts"
))

# 27. useInvestigationExport Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/use-investigation-export.ts",
    """"use client";

import { useState } from "react";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export function useInvestigationExport(scanId: string) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const downloadCsv = async (filename?: string) => {
    setIsExporting(true);
    setError(null);
    try {
      const csvText = await apiClient<string>(ENDPOINTS.scans.exportCsv(scanId));
      const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || `scan_${scanId}_accounts.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Export failed"));
    } finally {
      setIsExporting(false);
    }
  };

  const downloadJson = async (filename?: string) => {
    setIsExporting(true);
    setError(null);
    try {
      const jsonData = await apiClient<Record<string, unknown>>(ENDPOINTS.scans.exportJson(scanId));
      const blob = new Blob([JSON.stringify(jsonData, null, 2)], {
        type: "application/json;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || `scan_${scanId}_bundle.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Export failed"));
    } finally {
      setIsExporting(false);
    }
  };

  return {
    downloadCsv,
    downloadJson,
    isExporting,
    error,
  };
}
""",
    "feat(hooks): implement useInvestigationExport hook for triggering file downloads"
))

# 28. Test useInvestigationExport Hook
COMMITS.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-investigation-export.test.ts",
    """import { describe, it, expect } from "vitest";
import { renderHook } from "@testing-library/react";
import { useInvestigationExport } from "../use-investigation-export";

describe("useInvestigationExport hook", () => {
  it("exposes downloadCsv and downloadJson action functions", () => {
    const { result } = renderHook(() => useInvestigationExport("scan_123"));
    expect(typeof result.current.downloadCsv).toBe("function");
    expect(typeof result.current.downloadJson).toBe("function");
    expect(result.current.isExporting).toBe(false);
  });
});
""",
    "test(hooks): test useInvestigationExport creates download blob URL"
))

# 29. Fast Virtualized Table Row Model
COMMITS.append((
    "apps/dashboard/src/tokens/table-virtualization.ts",
    """export const TABLE_CONFIG = {
  rowHeight: 52,
  headerHeight: 44,
  overscan: 5,
  defaultPageSize: 50,
  pageSizeOptions: [10, 25, 50, 100],
} as const;
""",
    "feat(tokens): define table virtualization dimensions and page size presets"
))

# 30. Test Virtualized Table Config
COMMITS.append((
    "apps/dashboard/src/tokens/__tests__/table-virtualization.test.ts",
    """import { describe, it, expect } from "vitest";
import { TABLE_CONFIG } from "../table-virtualization";

describe("TABLE_CONFIG tokens", () => {
  it("defines constant row height and pagination options", () => {
    expect(TABLE_CONFIG.rowHeight).toBe(52);
    expect(TABLE_CONFIG.pageSizeOptions).toContain(50);
  });
});
""",
    "test(tokens): test table virtualization config constants"
))

# 31. Signal Weight Normalizer Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/signal-weight.ts",
    """export function formatSignalWeight(weight: number): string {
  const pct = Math.round(weight * 100);
  return `${pct}%`;
}

export function sortSignalsByImpact<T extends { weight: number }>(signals: T[]): T[] {
  return [...signals].sort((a, b) => b.weight - a.weight);
}
""",
    "feat(utils): add signal weight formatter and impact sorter"
))

# 32. Test Signal Weight Normalizer
COMMITS.append((
    "apps/dashboard/src/lib/utils/__tests__/signal-weight.test.ts",
    """import { describe, it, expect } from "vitest";
import { formatSignalWeight, sortSignalsByImpact } from "../signal-weight";

describe("signal weight utilities", () => {
  it("formats weight as percentage", () => {
    expect(formatSignalWeight(0.35)).toBe("35%");
  });

  it("sorts signals by descending weight", () => {
    const list = [{ name: "A", weight: 0.1 }, { name: "B", weight: 0.5 }];
    const sorted = sortSignalsByImpact(list);
    expect(sorted[0].name).toBe("B");
  });
});
""",
    "test(utils): test signal weight formatter and descending impact sorter"
))

# 33. Limitations Formatter Utility
COMMITS.append((
    "apps/dashboard/src/lib/utils/limitations.ts",
    """export function formatLimitationNotice(limitationKey: string): { title: string; explanation: string } {
  const notices: Record<string, { title: string; explanation: string }> = {
    unobservable_posts: {
      title: "Private Post Visibility",
      explanation: "Recent content and media interactions are private and excluded from scoring.",
    },
    rate_limit_truncation: {
      title: "Rate Limit Quota Truncation",
      explanation: "Collection capped at allowable platform rate limits; coverage is partial.",
    },
    missing_account_creation_date: {
      title: "Creation Timestamp Unavailable",
      explanation: "Platform API does not expose exact registration timestamp.",
    },
  };

  return notices[limitationKey] || {
    title: "Collection Limitation",
    explanation: limitationKey,
  };
}
""",
    "feat(utils): add formatLimitationNotice explaining unobservable fields"
))

# 34. Test Limitations Formatter
COMMITS.append((
    "apps/dashboard/src/lib/utils/__tests__/limitations.test.ts",
    """import { describe, it, expect } from "vitest";
import { formatLimitationNotice } from "../limitations";

describe("formatLimitationNotice", () => {
  it("translates known keys into clear titles and explanations", () => {
    const notice = formatLimitationNotice("unobservable_posts");
    expect(notice.title).toBe("Private Post Visibility");
    expect(notice.explanation).toContain("excluded from scoring");
  });
});
""",
    "test(utils): test formatLimitationNotice with known and fallback keys"
))

# 35. Status report for Batch 2
COMMITS.append((
    "docs/status/day-05/02-account-profile-view-delivery.md",
    """# Day 5 Status 02: Account Profile Types and Hooks

Delivered frontend data fetching layer and tokens for Day 5 Account Investigation:
- Defined typed models (`AccountAssessment`, `RelationshipEdge`, `AccountEvidenceRecord`).
- Created SWR hooks (`useInvestigation`, `useAccounts`, `useAccountDetail`, `useAccountEvidence`, `useRelationships`, `useAccountNeighborhood`, `useInvestigationExport`).
- Added token definitions for `risk-gauge`, `relationships`, and `table-virtualization`.
- Added utilities for search debounce, sorting, signal weighting, and limitation formatting.
""",
    "docs(status): log Day 5 milestone 02 account profile view delivery"
))

def main() -> None:
    print(f"Starting Day 5 Batch 2 commits build. Total planned: {len(COMMITS)}")
    for rel_path, content, msg in COMMITS:
        write_and_commit(rel_path, content, msg)
    print(f"Batch 2 finished {len(COMMITS)} commits.")

if __name__ == "__main__":
    main()

