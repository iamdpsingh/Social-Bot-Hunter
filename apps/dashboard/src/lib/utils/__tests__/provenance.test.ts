import { describe, it, expect } from "vitest";
import { isSyntheticObservation } from "../provenance";

describe("Provenance utility", () => {
  it("identifies synthetic records by flag or synthetic ID prefix", () => {
    expect(isSyntheticObservation({ is_synthetic: true })).toBe(true);
    expect(isSyntheticObservation({ account_id: "synth_user_01" })).toBe(true);
    expect(isSyntheticObservation({ account_id: "real_user_01" })).toBe(false);
  });
});
