import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import InvestigationGraphPage from "../page";

vi.mock("../../../../components/graph/graph-page-client", () => ({
  GraphPageClient: ({ scanId }: { scanId: string }) => (
    <div data-testid="mock-graph-client">Graph Client for {scanId}</div>
  ),
}));

describe("InvestigationGraphPage route", () => {
  it("renders GraphPageClient with route param id", () => {
    render(<InvestigationGraphPage params={{ id: "scan_123" }} />);
    expect(screen.getByTestId("mock-graph-client")).toBeInTheDocument();
    expect(screen.getByText("Graph Client for scan_123")).toBeInTheDocument();
  });
});
