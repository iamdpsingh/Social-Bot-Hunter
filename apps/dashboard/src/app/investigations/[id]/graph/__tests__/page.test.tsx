import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import InvestigationGraphPage from "../page";

describe("InvestigationGraphPage route", () => {
  it("renders GraphPageClient with route param id", () => {
    render(<InvestigationGraphPage params={{ id: "scan_123" }} />);
    expect(screen.getByTestId("graph-page-client")).toBeInTheDocument();
    expect(screen.getByText("scan_123")).toBeInTheDocument();
  });
});
