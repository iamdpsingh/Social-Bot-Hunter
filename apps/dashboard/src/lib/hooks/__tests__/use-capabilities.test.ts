import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useCapabilities } from "../use-capabilities";

vi.mock("../../api/client", () => ({
  apiClient: {
    getCapabilities: vi.fn().mockResolvedValue({
      platforms: {
        x: { name: "X", status: "implemented" },
        instagram: { name: "Instagram", status: "implemented" },
      },
    }),
  },
}));

describe("useCapabilities hook", () => {
  it("fetches platform capabilities matrix", async () => {
    const { result } = renderHook(() => useCapabilities());
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    expect(result.current.capabilities?.platforms.x.status).toBe("implemented");
  });
});
