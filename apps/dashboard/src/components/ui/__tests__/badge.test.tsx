import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import { Badge, RiskBadge, ScanStatusBadge } from "../badge";

describe("Badge components", () => {
  it("renders generic badge with text", () => {
    render(<Badge>Test Badge</Badge>);
    expect(screen.getByText("Test Badge")).toBeInTheDocument();
  });

  it("renders RiskBadge for critical score", () => {
    render(<RiskBadge score={0.85} />);
    expect(screen.getByText(/critical risk/i)).toBeInTheDocument();
    expect(screen.getByText("(85%)")).toBeInTheDocument();
  });

  it("renders RiskBadge for low score", () => {
    render(<RiskBadge score={0.15} />);
    expect(screen.getByText(/low risk/i)).toBeInTheDocument();
    expect(screen.getByText("(15%)")).toBeInTheDocument();
  });

  it("renders RiskBadge for insufficient evidence when score is null", () => {
    render(<RiskBadge score={null} />);
    expect(screen.getByText(/insufficient evidence/i)).toBeInTheDocument();
  });

  it("renders ScanStatusBadge for each lifecycle state", () => {
    const { rerender } = render(<ScanStatusBadge status="running" />);
    expect(screen.getByText("Running")).toBeInTheDocument();

    rerender(<ScanStatusBadge status="complete" />);
    expect(screen.getByText("Complete")).toBeInTheDocument();

    rerender(<ScanStatusBadge status="failed" />);
    expect(screen.getByText("Failed")).toBeInTheDocument();

    rerender(<ScanStatusBadge status="pending" />);
    expect(screen.getByText("Pending")).toBeInTheDocument();
  });
});
