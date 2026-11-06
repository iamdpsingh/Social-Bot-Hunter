import { describe, expect, it } from "vitest";
import { matchNodeSearch } from "../search";

describe("matchNodeSearch", () => {
  const node = {
    id: "acc_1001",
    label: "SuspiciousBot_42",
    username: "crypto_bot_daily",
    cluster_id: "cluster_alpha",
  };

  it("matches on ID", () => {
    expect(matchNodeSearch(node, "1001")).toBe(true);
    expect(matchNodeSearch(node, "9999")).toBe(false);
  });

  it("matches on label and username", () => {
    expect(matchNodeSearch(node, "Suspicious")).toBe(true);
    expect(matchNodeSearch(node, "crypto")).toBe(true);
  });

  it("matches on cluster ID", () => {
    expect(matchNodeSearch(node, "alpha")).toBe(true);
  });

  it("returns true for empty query", () => {
    expect(matchNodeSearch(node, "")).toBe(true);
    expect(matchNodeSearch(node, "   ")).toBe(true);
  });
});
