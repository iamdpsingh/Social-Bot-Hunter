import { describe, it, expect, beforeEach, vi } from "vitest";
import { apiClient, setAuthToken, getAuthToken, ApiError } from "../client";

describe("apiClient utility", () => {
  beforeEach(() => {
    setAuthToken(null);
    vi.restoreAllMocks();
  });

  it("sets and gets auth token", () => {
    setAuthToken("jwt_test_token");
    expect(getAuthToken()).toBe("jwt_test_token");
  });

  it("attaches Authorization header when token is present", async () => {
    setAuthToken("sample_token_xyz");

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok" }),
    });
    global.fetch = mockFetch;

    await apiClient("http://localhost:8080/api/v1/health");

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const headers = mockFetch.mock.calls[0][1].headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer sample_token_xyz");
    expect(headers.get("Content-Type")).toBe("application/json");
  });

  it("throws ApiError with status and parsed detail on failure", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: "Scan 'missing-id' not found" }),
    });

    await expect(apiClient("http://localhost:8080/api/v1/scans/missing-id")).rejects.toThrow(
      "Scan 'missing-id' not found"
    );
  });
});
