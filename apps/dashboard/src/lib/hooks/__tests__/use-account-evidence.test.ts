import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccountEvidence } from "../use-account-evidence";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      account_id: "a1",
      evidence: [
        { id: "e1", evidence_type: "heuristic", summary: "High follow rate", details: {} },
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccountEvidence hook", () => {
  it("fetches concrete evidence items", () => {
    const { result } = renderHook(() => useAccountEvidence("s1", "a1"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.evidence).toHaveLength(1);
    expect(result.current.evidence[0].summary).toBe("High follow rate");
  });
});
