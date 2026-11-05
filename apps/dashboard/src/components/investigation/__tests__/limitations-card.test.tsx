import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LimitationsCard } from "../limitations-card";

describe("LimitationsCard component", () => {
  it("renders coverage percentage and limitation explanations", () => {
    render(
      <LimitationsCard
        coveragePct={65}
        limitations={["unobservable_posts"]}
      />
    );
    expect(screen.getByText("Coverage: 65%")).toBeInTheDocument();
    expect(screen.getByText("Private Post Visibility")).toBeInTheDocument();
  });
});
