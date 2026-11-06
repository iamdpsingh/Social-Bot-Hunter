import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useGraphClusters } from "../use-graph-clusters";

describe("useGraphClusters hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_10",
          clusters: [
            { id: "c_1", method: "wcc", member_count: 5, confidence: "high", signal_strength: "strong", members: ["m1"] },
          ],
          total: 1,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads clusters list for scan", async () => {
    const { result } = renderHook(() => useGraphClusters("scan_10"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.clusters).toHaveLength(1);
    expect(result.current.clusters[0].id).toBe("c_1");
  });
});
