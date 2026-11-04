import { describe, it, expect, vi } from "vitest";
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
