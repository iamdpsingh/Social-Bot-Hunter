import { describe, it, expect, vi } from "vitest";
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
