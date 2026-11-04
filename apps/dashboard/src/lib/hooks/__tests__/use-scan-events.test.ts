import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useScanEvents } from "../use-scan-events";

describe("useScanEvents hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "EventSource",
      vi.fn().mockImplementation(() => ({
        onmessage: null,
        onerror: null,
        close: vi.fn(),
      }))
    );
  });

  it("subscribes to scan event stream when scanId is provided", () => {
    const { result } = renderHook(() => useScanEvents("scan_123"));
    expect(result.current.isConnected).toBe(true);
    expect(result.current.events).toEqual([]);
  });
});
