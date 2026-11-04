import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useHealth } from "../use-health";
import { apiClient } from "../../api/client";

vi.mock("../../api/client", () => ({
  apiClient: {
    getHealth: vi.fn().mockResolvedValue({ status: "ok", version: "0.1.0", database: "connected" }),
  },
}));

describe("useHealth hook", () => {
  it("fetches system health and database status", async () => {
    const { result } = renderHook(() => useHealth());
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    expect(result.current.health?.status).toBe("ok");
    expect(result.current.health?.database).toBe("connected");
  });
});
