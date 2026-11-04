import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useAudit } from "../use-audit";

vi.mock("../../api/client", () => ({
  apiClient: {
    listAuditEvents: vi.fn().mockResolvedValue({
      items: [
        {
          id: "audit_1",
          actor_id: "user_analyst_1",
          action: "scan.create",
          timestamp: "2026-11-04T12:00:00Z",
        },
      ],
      total: 1,
    }),
  },
}));

describe("useAudit hook", () => {
  it("fetches audit log events list", async () => {
    const { result } = renderHook(() => useAudit({ limit: 5 }));
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    expect(result.current.audit?.items).toHaveLength(1);
    expect(result.current.audit?.items[0].action).toBe("scan.create");
  });
});
