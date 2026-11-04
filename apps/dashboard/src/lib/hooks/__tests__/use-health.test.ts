import { describe, it, expect, vi } from "vitest";
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
