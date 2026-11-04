import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useScans } from "../use-scans";

vi.mock("../../api/client", () => ({
  apiClient: {
    listScans: vi.fn().mockResolvedValue({
      items: [
        {
          id: "scan_01",
          platform: "x",
          target_username: "elonmusk",
          status: "completed",
          created_at: "2026-11-04T10:00:00Z",
        },
      ],
      total: 1,
      limit: 10,
      offset: 0,
    }),
  },
}));

describe("useScans hook", () => {
  it("fetches scan list and returns items", async () => {
    const { result } = renderHook(() => useScans({ limit: 10 }));
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    expect(result.current.scans?.items).toHaveLength(1);
    expect(result.current.scans?.items[0].target_username).toBe("elonmusk");
  });
});
