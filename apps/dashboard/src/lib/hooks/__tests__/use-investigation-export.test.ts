import { describe, it, expect } from "vitest";
import { renderHook } from "@testing-library/react";
import { useInvestigationExport } from "../use-investigation-export";

describe("useInvestigationExport hook", () => {
  it("exposes downloadCsv and downloadJson action functions", () => {
    const { result } = renderHook(() => useInvestigationExport("scan_123"));
    expect(typeof result.current.downloadCsv).toBe("function");
    expect(typeof result.current.downloadJson).toBe("function");
    expect(result.current.isExporting).toBe(false);
  });
});
