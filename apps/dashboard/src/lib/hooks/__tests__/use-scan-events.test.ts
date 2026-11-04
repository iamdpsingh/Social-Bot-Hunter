import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useScanEvents } from "../use-scan-events";

describe("useScanEvents hook", () => {
  let createdEventSource: any = null;

  beforeEach(() => {
    vi.stubGlobal(
      "EventSource",
      vi.fn().mockImplementation((url: string) => {
        createdEventSource = {
          url,
          onopen: null,
          onmessage: null,
          onerror: null,
          close: vi.fn(),
        };
        return createdEventSource;
      })
    );
  });

  it("subscribes to scan event stream and updates on open", () => {
    const { result } = renderHook(() => useScanEvents("scan_123"));
    expect(result.current.isConnected).toBe(false);

    act(() => {
      createdEventSource.onopen();
    });

    expect(result.current.isConnected).toBe(true);
  });
});
