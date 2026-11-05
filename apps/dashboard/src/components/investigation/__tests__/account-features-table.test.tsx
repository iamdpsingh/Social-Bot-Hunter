import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountFeaturesTable } from "../account-features-table";

describe("AccountFeaturesTable component", () => {
  it("renders feature rows and availability status tags", () => {
    const features: any[] = [
      { feature_name: "follow_burst", category: "temporal", value: 0.9412, is_available: true },
    ];
    render(<AccountFeaturesTable features={features} />);
    expect(screen.getByText("follow_burst")).toBeInTheDocument();
    expect(screen.getByText("temporal")).toBeInTheDocument();
    expect(screen.getByText("0.9412")).toBeInTheDocument();
    expect(screen.getByText("Available")).toBeInTheDocument();
  });
});
