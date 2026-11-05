import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccountDetail } from "../use-account-detail";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      account_id: "acc_1",
      assessment: { id: "ass_1", score: 0.85, band: "critical" },
      profile_observation: { username: "suspicious_user" },
      features: [{ feature_name: "default_avatar", value: 1.0 }],
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccountDetail hook", () => {
  it("returns detailed assessment, observation, and features", () => {
    const { result } = renderHook(() => useAccountDetail("s1", "acc_1"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.assessment?.score).toBe(0.85);
    expect(result.current.observation?.username).toBe("suspicious_user");
  });
});
