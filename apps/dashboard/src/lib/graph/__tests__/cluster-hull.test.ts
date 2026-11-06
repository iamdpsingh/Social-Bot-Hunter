import { describe, expect, it } from "vitest";
import { computeConvexHull, crossProduct } from "../cluster-hull";

describe("cluster hull algorithms", () => {
  it("calculates 2D cross product", () => {
    const o = { x: 0, y: 0 };
    const a = { x: 1, y: 0 };
    const b = { x: 0, y: 1 };
    expect(crossProduct(o, a, b)).toBe(1);
  });

  it("computes convex hull of a point set", () => {
    const points = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 10 },
      { x: 0, y: 10 },
      { x: 5, y: 5 }, // interior point
    ];
    const hull = computeConvexHull(points);
    expect(hull).toHaveLength(4);
    expect(hull.some((p) => p.x === 5 && p.y === 5)).toBe(false);
  });

  it("handles small point sets safely", () => {
    expect(computeConvexHull([])).toEqual([]);
    expect(computeConvexHull([{ x: 1, y: 2 }])).toEqual([{ x: 1, y: 2 }]);
  });
});
