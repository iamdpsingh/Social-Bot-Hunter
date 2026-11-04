import { describe, it, expect, vi } from "vitest";
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
