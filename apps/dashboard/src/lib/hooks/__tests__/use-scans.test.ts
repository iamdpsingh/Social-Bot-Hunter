import { describe, it, expect, vi } from "vitest";
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
