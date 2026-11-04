import { describe, it, expect } from "vitest";
import { transformToGraphElements } from "../network-transform";

describe("Network Transform utility", () => {
  it("converts nodes and edges into graph element dictionaries", () => {
    const nodes = [{ id: "n1", label: "@user1", platform: "x", riskScore: 80 }];
    const edges = [{ source: "n1", target: "n2", relationshipType: "follows" }];
    const elements = transformToGraphElements(nodes, edges);

    expect(elements).toHaveLength(2);
    expect(elements[0].data.id).toBe("n1");
    const edgeData = elements[1].data as { source: string; target: string; type: string };
    expect(edgeData.source).toBe("n1");
  });
});
