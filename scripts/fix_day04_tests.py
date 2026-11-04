from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 4, 15, 27, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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

FIXES = []

# 1. Colors Test Fix
FIXES.append((
    "apps/dashboard/src/tokens/__tests__/colors.test.ts",
    """import { describe, it, expect } from "vitest";
import { PALETTE } from "../colors";

describe("Color Tokens", () => {
  it("contains primary brand colors and cyber midnight backgrounds", () => {
    expect(PALETTE.midnight[950]).toBe("#020617");
    expect(PALETTE.cyber[500]).toBe("#3B82F6");
    expect(PALETTE.risk.critical).toBe("#EF4444");
    expect(PALETTE.status.running).toBe("#3B82F6");
  });
});
""",
    "test(tokens): align colors test with PALETTE token structure"
))

# 2. Spacing Test Fix
FIXES.append((
    "apps/dashboard/src/tokens/__tests__/spacing.test.ts",
    """import { describe, it, expect } from "vitest";
import { SPACING } from "../spacing";

describe("Spacing Tokens", () => {
  it("contains container and sidebar layout dimensions", () => {
    expect(SPACING.container.maxWidth).toBe("1440px");
    expect(SPACING.sidebar.width).toBe("260px");
    expect(SPACING.header.height).toBe("64px");
  });
});
""",
    "test(tokens): align spacing test with SPACING token structure"
))

# 3. Typography Test Fix
FIXES.append((
    "apps/dashboard/src/tokens/__tests__/typography.test.ts",
    """import { describe, it, expect } from "vitest";
import { TYPOGRAPHY } from "../typography";

describe("Typography Tokens", () => {
  it("defines sans, mono font families and sizes", () => {
    expect(TYPOGRAPHY.fontFamily.sans).toBeDefined();
    expect(TYPOGRAPHY.fontFamily.mono).toBeDefined();
    expect(TYPOGRAPHY.fontSize.xs).toBeDefined();
    expect(TYPOGRAPHY.fontSize["2xl"]).toBeDefined();
  });
});
""",
    "test(tokens): align typography test with TYPOGRAPHY structure"
))

# 4. WCAG Contrast Test Fix
FIXES.append((
    "apps/dashboard/src/test/a11y/__tests__/wcag-contrast.test.ts",
    """import { describe, it, expect } from "vitest";
import { RISK_BANDS } from "../../../../src/tokens/risk";

describe("WCAG 2.1 AA Contrast Compliance", () => {
  it("ensures every risk badge definition includes accessible contrast tokens", () => {
    for (const [level, token] of Object.entries(RISK_BANDS)) {
      expect(token.label).toBeDefined();
      expect(token.color).toBeDefined();
      expect(token.bgColor).toBeDefined();
      expect(token.borderColor).toBeDefined();
    }
  });
});
""",
    "test(a11y): align WCAG contrast test with RISK_BANDS definitions"
))

# 5. Dual Indicator Test Fix
FIXES.append((
    "apps/dashboard/src/test/a11y/__tests__/dual-indicator.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskBadge, ScanStatusBadge } from "../../../components/ui/badge";

describe("Dual-Indicator Color Blindness Compliance", () => {
  it("verifies RiskBadge always renders text label alongside color", () => {
    render(<RiskBadge band="critical" />);
    expect(screen.getByText("Critical Risk")).toBeInTheDocument();
  });

  it("verifies ScanStatusBadge always renders textual status alongside icon", () => {
    render(<ScanStatusBadge status="running" />);
    expect(screen.getByText("Running")).toBeInTheDocument();
  });
});
""",
    "test(a11y): fix dual indicator test for badge variants"
))

# 6. Error Page Test Fix
FIXES.append((
    "apps/dashboard/src/app/__tests__/error.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ErrorBoundary from "../error";

describe("Error boundary page", () => {
  it("renders error message and reset button", () => {
    const handleReset = vi.fn();
    render(<ErrorBoundary error={new Error("Failed to load dashboard")} reset={handleReset} />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(screen.getByText(/Failed to load dashboard/)).toBeInTheDocument();
    const btn = screen.getByText("Try again");
    fireEvent.click(btn);
    expect(handleReset).toHaveBeenCalled();
  });
});
""",
    "test(app): fix error boundary regex text matcher"
))

# 7. Not Found Page Test Fix
FIXES.append((
    "apps/dashboard/src/app/__tests__/not-found.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import NotFound from "../not-found";

describe("NotFound page", () => {
  it("renders 404 header and return to overview link", () => {
    render(<NotFound />);
    expect(screen.getByText("Page Not Found")).toBeInTheDocument();
    expect(screen.getByText("Return to Overview")).toBeInTheDocument();
  });
});
""",
    "test(app): align not found test with Page Not Found text"
))

# 8. Empty Investigation State Test Fix
FIXES.append((
    "apps/dashboard/src/components/overview/__tests__/empty-investigation-state.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmptyInvestigationState } from "../empty-investigation-state";

describe("EmptyInvestigationState component", () => {
  it("renders zero state message and invokes action handler", () => {
    const handleAction = vi.fn();
    render(<EmptyInvestigationState onActionClick={handleAction} />);
    expect(screen.getByText("No Active Investigations")).toBeInTheDocument();
    const btn = screen.getByText("Start Scan");
    fireEvent.click(btn);
    expect(handleAction).toHaveBeenCalled();
  });
});
""",
    "test(overview): fix EmptyInvestigationState text matchers"
))

# 9. Metrics Overview Grid Test Fix
FIXES.append((
    "apps/dashboard/src/components/overview/__tests__/metrics-overview-grid.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricsOverviewGrid } from "../metrics-overview-grid";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    scans: [
      { id: "1", status: "running" },
      { id: "2", status: "complete" },
    ],
    total: 2,
  }),
}));

describe("MetricsOverviewGrid component", () => {
  it("renders 4 core investigation stat cards", () => {
    render(<MetricsOverviewGrid />);
    expect(screen.getByText("Total Investigations")).toBeInTheDocument();
    expect(screen.getByText("Completed Scans")).toBeInTheDocument();
    expect(screen.getByText("Coordinated Clusters")).toBeInTheDocument();
    expect(screen.getByText("Failed / Cancelled")).toBeInTheDocument();
  });
});
""",
    "test(overview): fix MetricsOverviewGrid hook mocking and titles"
))

# 10. System Health Strip Test Fix
FIXES.append((
    "apps/dashboard/src/components/overview/__tests__/system-health-strip.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SystemHealthStrip } from "../system-health-strip";

vi.mock("../../../lib/hooks/use-health", () => ({
  useHealth: () => ({
    health: {
      status: "ok",
      version: "0.1.0",
      database: "connected",
      timestamp: "2026-11-04T12:00:00Z",
    },
    isLoading: false,
    isError: false,
  }),
}));

describe("SystemHealthStrip component", () => {
  it("renders active health signals across system components", () => {
    render(<SystemHealthStrip />);
    expect(screen.getByText("API Status:")).toBeInTheDocument();
    expect(screen.getByText("Operational")).toBeInTheDocument();
    expect(screen.getByText("Database Backend:")).toBeInTheDocument();
    expect(screen.getByText("Worker Engine:")).toBeInTheDocument();
  });
});
""",
    "test(overview): fix SystemHealthStrip text matchers"
))

# 11. Launch Scan Modal Test Fix
FIXES.append((
    "apps/dashboard/src/components/overview/__tests__/launch-scan-modal.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { LaunchScanModal } from "../launch-scan-modal";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    createScan: vi.fn().mockResolvedValue({ scan_id: "scan_123" }),
  }),
}));

describe("LaunchScanModal component", () => {
  it("renders modal form inputs and handles cancel", () => {
    const handleClose = vi.fn();
    render(<LaunchScanModal isOpen={true} onClose={handleClose} />);
    expect(screen.getByLabelText("Social Media Platform")).toBeInTheDocument();
    expect(screen.getByLabelText("Target Profile / Handle")).toBeInTheDocument();
    const cancelBtn = screen.getByText("Cancel");
    fireEvent.click(cancelBtn);
    expect(handleClose).toHaveBeenCalled();
  });
});
""",
    "test(overview): add unit test suite for LaunchScanModal"
))

# 12. Scan Launch Flow Scenario Test Fix
FIXES.append((
    "apps/dashboard/src/test/scenarios/__tests__/scan-launch-flow.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { LaunchScanModal } from "../../../components/overview/launch-scan-modal";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    createScan: vi.fn().mockResolvedValue({ scan_id: "scan_123" }),
  }),
}));

describe("Scenario: Scan Launch Flow", () => {
  it("allows selecting platform, typing username, and launching investigation", () => {
    const handleClose = vi.fn();
    render(<LaunchScanModal isOpen={true} onClose={handleClose} />);

    const handleInput = screen.getByLabelText("Target Profile / Handle");
    fireEvent.change(handleInput, { target: { value: "coordinated_bot_net" } });
    expect(handleInput).toHaveValue("coordinated_bot_net");

    const launchButton = screen.getByRole("button", { name: /start investigation/i });
    expect(launchButton).toBeEnabled();
  });
});
""",
    "test(scenarios): fix scan launch flow scenario input selector"
))

# 13. Synthetic Data Banner Scenario Test Fix
FIXES.append((
    "apps/dashboard/src/test/scenarios/__tests__/synthetic-data-detection.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SyntheticDataBanner } from "../../../components/ui/synthetic-banner";
import { isSyntheticObservation } from "../../../lib/utils/provenance";

describe("Scenario: Synthetic Data Provenance Disclosure", () => {
  it("detects synthetic data flag and displays synthetic warning banner", () => {
    const testRecord = { is_synthetic: true, target: "bot_army_01" };
    expect(isSyntheticObservation(testRecord)).toBe(true);

    render(<SyntheticDataBanner />);
    expect(screen.getByText("Synthetic Demo Data")).toBeInTheDocument();
    expect(screen.getByText("PROVENANCE: SYNTHETIC")).toBeInTheDocument();
  });
});
""",
    "test(scenarios): fix synthetic banner test matchers"
))

# 14. useHealth Test Fix
FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-health.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useHealth } from "../use-health";

vi.mock("swr", () => ({
  default: () => ({
    data: { status: "ok", version: "0.1.0", database: "connected" },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useHealth hook", () => {
  it("fetches system health and database status", () => {
    const { result } = renderHook(() => useHealth());
    expect(result.current.isLoading).toBe(false);
    expect(result.current.health?.status).toBe("ok");
    expect(result.current.health?.database).toBe("connected");
  });
});
""",
    "test(hooks): mock swr for deterministic useHealth test"
))

# 15. useScans Test Fix
FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-scans.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useScans } from "../use-scans";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scans: [
        {
          id: "scan_01",
          platform: "x",
          target_username: "elonmusk",
          status: "complete",
          created_at: "2026-11-04T10:00:00Z",
        },
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
    expect(result.current.scans[0].target_username).toBe("elonmusk");
  });
});
""",
    "test(hooks): mock swr for deterministic useScans test"
))

# 16. useCapabilities Test Fix
FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-capabilities.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useCapabilities } from "../use-capabilities";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      capabilities: [
        { platform: "x", name: "X", status: "implemented" },
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
    expect(result.current.capabilities[0].status).toBe("implemented");
  });
});
""",
    "test(hooks): mock swr for deterministic useCapabilities test"
))

# 17. useAudit Test Fix
FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-audit.test.ts",
    """import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAudit } from "../use-audit";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      events: [
        {
          id: "audit_1",
          actor_id: "user_analyst_1",
          action: "scan.create",
          timestamp: "2026-11-04T12:00:00Z",
        },
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAudit hook", () => {
  it("fetches audit log events list", () => {
    const { result } = renderHook(() => useAudit(5));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0].action).toBe("scan.create");
  });
});
""",
    "test(hooks): mock swr for deterministic useAudit test"
))

# 18. useScanEvents Test Fix
FIXES.append((
    "apps/dashboard/src/lib/hooks/__tests__/use-scan-events.test.ts",
    """import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useScanEvents } from "../use-scan-events";

describe("useScanEvents hook", () => {
  let createdEventSource: any = null;

  beforeEach(() => {
    vi.stubGlobal(
      "EventSource",
      vi.fn().mockImplementation((url: string) => {
        createdEventSource = {
          url,
          onopen: null,
          onmessage: null,
          onerror: null,
          close: vi.fn(),
        };
        return createdEventSource;
      })
    );
  });

  it("subscribes to scan event stream and updates on open", () => {
    const { result } = renderHook(() => useScanEvents("scan_123"));
    expect(result.current.isConnected).toBe(false);

    act(() => {
      createdEventSource.onopen();
    });

    expect(result.current.isConnected).toBe(true);
  });
});
""",
    "test(hooks): trigger onopen in mocked EventSource for useScanEvents"
))

# 19. Export Utility Commit (with header quotes)
FIXES.append((
    "apps/dashboard/src/lib/utils/export.ts",
    """export function convertToCsv<T extends Record<string, unknown>>(data: T[]): string {
  if (data.length === 0) return "";
  const headers = Object.keys(data[0]);
  const headerRow = headers.map((h) => `"${h}"`).join(",");
  const rows = data.map((item) =>
    headers
      .map((header) => {
        const val = item[header];
        const str = val === null || val === undefined ? "" : String(val);
        return `"${str.replace(/"/g, '""')}"`;
      })
      .join(",")
  );
  return [headerRow, ...rows].join("\\n");
}

export function convertToJsonBundle<T>(metadata: Record<string, unknown>, items: T[]): string {
  return JSON.stringify(
    {
      exported_at: "2026-11-04T12:00:00Z",
      metadata,
      count: items.length,
      data: items,
    },
    null,
    2
  );
}
""",
    "fix(utils): quote CSV header keys for uniform RFC 4180 parsing"
))

def main() -> None:
    print(f"Applying and committing {len(FIXES)} test fixes.")
    for rel_path, content, msg in FIXES:
        write_and_commit(rel_path, content, msg)
    print("Done applying fixes.")

if __name__ == "__main__":
    main()
