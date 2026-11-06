import { describe, expect, it, vi } from "vitest";
import { exportGraphJson, exportGraphPng } from "../export";

describe("graph export utilities", () => {
  it("triggers JSON file download from cytoscape instance", () => {
    const mockCy: any = {
      json: () => ({ elements: { nodes: [], edges: [] } }),
    };

    const createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    const revokeObjectURL = vi.fn();
    (global as any).URL.createObjectURL = createObjectURL;
    (global as any).URL.revokeObjectURL = revokeObjectURL;

    exportGraphJson(mockCy, "test.json");
    expect(createObjectURL).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
  });

  it("triggers PNG snapshot export from cytoscape instance", () => {
    const mockBlob = new Blob([]);
    const mockCy: any = {
      png: vi.fn().mockReturnValue(mockBlob),
    };

    const createObjectURL = vi.fn().mockReturnValue("blob:mock-png");
    const revokeObjectURL = vi.fn();
    (global as any).URL.createObjectURL = createObjectURL;
    (global as any).URL.revokeObjectURL = revokeObjectURL;

    exportGraphPng(mockCy, "test.png");
    expect(mockCy.png).toHaveBeenCalledWith(
      expect.objectContaining({ full: true, scale: 2, bg: "#ffffff" })
    );
  });
});
