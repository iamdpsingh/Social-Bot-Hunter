import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceInspector } from "../../../components/investigation/evidence-inspector";

describe("Scenario: Evidence Inspector Deconstruction", () => {
  it("collapses and expands supporting heuristic evidence rows", () => {
    const evidence = [
      { id: "ev_1", rule_name: "default_avatar", weight: 0.3, score: 1.0, summary: "Stock avatar detected" },
      { id: "ev_2", rule_name: "following_ratio", weight: 0.5, score: 0.9, summary: "Extreme out-degree ratio" },
    ];

    render(<EvidenceInspector evidence={evidence} />);

    expect(screen.getByText("default_avatar")).toBeInTheDocument();
    expect(screen.getByText("following_ratio")).toBeInTheDocument();

    // Toggle collapse
    const toggleBtn = screen.getByRole("button", { name: /Toggle Evidence/i });
    fireEvent.click(toggleBtn);
    expect(screen.queryByText("default_avatar")).not.toBeInTheDocument();

    // Re-expand
    fireEvent.click(toggleBtn);
    expect(screen.getByText("default_avatar")).toBeInTheDocument();
  });
});
