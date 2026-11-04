import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useCapabilities } from "../use-capabilities";
import type { PlatformCapability } from "../../api/types";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      capabilities: [
        {
          platform: "x",
          operation: "read_profile",
          supported: true,
          required_permissions: ["users.read"],
        } as PlatformCapability,
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useCapabilities hook", () => {
  it("fetches platform capabilities list", () => {
    const { result } = renderHook(() => useCapabilities());
    expect(result.current.isLoading).toBe(false);
    expect(result.current.capabilities).toHaveLength(1);
    expect(result.current.capabilities[0].supported).toBe(true);
  });
});
