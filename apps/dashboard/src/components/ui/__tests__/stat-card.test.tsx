import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import { StatCard } from "../stat-card";
import { Activity } from "lucide-react";

describe("StatCard component", () => {
  it("renders title, value, and description", () => {
    render(
      <StatCard
        title="Total Scans"
        value={42}
        description="Active jobs"
        icon={Activity}
        coveragePct={88}
        trend={{ value: "+5%", isPositive: true }}
      />
    );

    expect(screen.getByText("Total Scans")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Active jobs")).toBeInTheDocument();
    expect(screen.getByText("88% coverage")).toBeInTheDocument();
    expect(screen.getByText("+5%")).toBeInTheDocument();
  });
});
