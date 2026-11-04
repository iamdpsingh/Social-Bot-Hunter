import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskBadge, ScanStatusBadge } from "../../../components/ui/badge";

describe("Dual-Indicator Color Blindness Compliance", () => {
  it("verifies RiskBadge always renders text label alongside color", () => {
    render(<RiskBadge band="critical" />);
    expect(screen.getByText("Critical Risk")).toBeInTheDocument();
  });

  it("verifies ScanStatusBadge always renders textual status alongside icon", () => {
    render(<ScanStatusBadge status="running" />);
    expect(screen.getByText("Running")).toBeInTheDocument();
  });
});
