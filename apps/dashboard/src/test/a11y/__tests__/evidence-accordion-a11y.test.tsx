import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceInspector } from "../../../components/investigation/evidence-inspector";

describe("EvidenceInspector Accessibility", () => {
  it("exposes aria-expanded state and keyboard toggleability", () => {
    const evidence = [
      {
        id: "ev_1",
        rule_name: "default_avatar",
        weight: 0.25,
        score: 1.0,
        summary: "Default avatar placeholder in use",
      },
    ];

    render(<EvidenceInspector evidence={evidence} />);
    const toggleButton = screen.getByRole("button", { name: /Toggle Evidence/i });
    expect(toggleButton).toHaveAttribute("aria-expanded", "true");

    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute("aria-expanded", "false");
  });
});
