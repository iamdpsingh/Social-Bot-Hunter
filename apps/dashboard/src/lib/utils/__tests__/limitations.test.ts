import { describe, it, expect } from "vitest";
import { formatLimitationNotice } from "../limitations";

describe("formatLimitationNotice", () => {
  it("translates known keys into clear titles and explanations", () => {
    const notice = formatLimitationNotice("unobservable_posts");
    expect(notice.title).toBe("Private Post Visibility");
    expect(notice.explanation).toContain("excluded from scoring");
  });
});
