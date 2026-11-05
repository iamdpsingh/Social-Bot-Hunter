import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccounts } from "../use-accounts";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "scan_10",
      total: 1,
      offset: 0,
      limit: 50,
      accounts: [
        {
          id: "a1",
          pid: "p1",
          platform_account_id: "p1",
          username: "bot_1",
          score: 0.9,
          band: "critical",
        },
      ],
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccounts hook", () => {
  it("fetches paginated accounts with risk scores", () => {
    const { result } = renderHook(() => useAccounts("scan_10", { limit: 50 }));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.accounts).toHaveLength(1);
    expect(result.current.accounts[0].score).toBe(0.9);
  });
});
