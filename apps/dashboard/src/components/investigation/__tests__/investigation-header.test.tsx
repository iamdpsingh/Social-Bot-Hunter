import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { InvestigationHeader } from "../investigation-header";

describe("InvestigationHeader component", () => {
  it("renders scan title, target, and status badge", () => {
    const scan: any = {
      id: "scan_123",
      platform: "x",
      status: "complete",
      requested_by: "analyst_1",
      created_at: "2026-11-05T09:00:00Z",
      collection_mode: "official_api",
      data_origin: "api",
    };
    render(<InvestigationHeader scan={scan} />);
    expect(screen.getByText("Investigation: analyst_1")).toBeInTheDocument();
    expect(screen.getByText("Back to Overview")).toBeInTheDocument();
    expect(screen.getByText("Complete")).toBeInTheDocument();
  });
});
