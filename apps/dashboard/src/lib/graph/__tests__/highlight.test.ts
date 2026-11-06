import { describe, expect, it, vi } from "vitest";
import { highlightNodeAndNeighbors } from "../highlight";

describe("highlightNodeAndNeighbors", () => {
  it("clears highlights when nodeId is null", () => {
    const mockElements = {
      removeClass: vi.fn(),
    };
    const mockCy: any = {
      batch: (fn: any) => fn(),
      elements: () => mockElements,
    };

    highlightNodeAndNeighbors(mockCy, null);
    expect(mockElements.removeClass).toHaveBeenCalledWith("highlighted dimmed");
  });

  it("highlights focal node and neighborhood while dimming others", () => {
    const mockNeighborhood = {
      addClass: vi.fn().mockReturnThis(),
      removeClass: vi.fn().mockReturnThis(),
    };
    const mockFocal = {
      length: 1,
      neighborhood: () => ({
        add: () => mockNeighborhood,
      }),
    };
    const mockNonNeighborhood = {
      addClass: vi.fn().mockReturnThis(),
      removeClass: vi.fn().mockReturnThis(),
    };
    const mockAll = {
      difference: () => mockNonNeighborhood,
    };

    const mockCy: any = {
      batch: (fn: any) => fn(),
      $id: vi.fn().mockReturnValue(mockFocal),
      elements: () => mockAll,
    };

    highlightNodeAndNeighbors(mockCy, "focal_node");
    expect(mockCy.$id).toHaveBeenCalledWith("focal_node");
    expect(mockNeighborhood.addClass).toHaveBeenCalledWith("highlighted");
    expect(mockNonNeighborhood.addClass).toHaveBeenCalledWith("dimmed");
  });
});
