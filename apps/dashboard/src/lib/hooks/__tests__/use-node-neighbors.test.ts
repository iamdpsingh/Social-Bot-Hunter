import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useNodeNeighbors } from "../use-node-neighbors";

describe("useNodeNeighbors hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_1",
          center_node_id: "acc_1",
          direction: "both",
          radius: 1,
          neighbors: [
            { node_id: "acc_2", direction: "inbound", relationship_type: "follower", risk_score: 0.88, risk_band: "high" },
          ],
          total: 1,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches neighbors when focal nodeId is provided", async () => {
    const { result } = renderHook(() => useNodeNeighbors("scan_1", "acc_1"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.neighbors).toHaveLength(1);
    expect(result.current.data?.center_node_id).toBe("acc_1");
  });

  it("does not fetch when nodeId is null", () => {
    const { result } = renderHook(() => useNodeNeighbors("scan_1", null));
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
  });
});
