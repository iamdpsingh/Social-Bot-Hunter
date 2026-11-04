import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EvidenceBadge } from "../evidence-badge";

describe("EvidenceBadge component", () => {
  it("renders label and percentage confidence score", () => {
    render(<EvidenceBadge label="Temporal Burst" confidence={0.88} />);
    expect(screen.getByText("Temporal Burst")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
  });
});
