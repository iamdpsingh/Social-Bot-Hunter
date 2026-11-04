import { describe, it, expect } from "vitest";
import { convertToCsv, convertToJsonBundle } from "../export";

describe("Export utility", () => {
  it("converts objects array to CSV string with quotes", () => {
    const items = [
      { id: "1", target: "user1", score: 85 },
      { id: "2", target: "user2", score: 12 },
    ];
    const csv = convertToCsv(items);
    expect(csv).toContain('"id","target","score"');
    expect(csv).toContain('"1","user1","85"');
  });

  it("packages json bundle with export metadata", () => {
    const bundle = convertToJsonBundle({ scan_id: "scan_01" }, [{ id: "1" }]);
    const parsed = JSON.parse(bundle);
    expect(parsed.count).toBe(1);
    expect(parsed.metadata.scan_id).toBe("scan_01");
  });
});
