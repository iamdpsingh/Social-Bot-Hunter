import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AdapterTelemetryTable } from "../../../components/adapters/adapter-telemetry-table";
import { AdapterTelemetryRecord } from "../../../lib/api/types";

describe("Scenario: Adapter Telemetry Monitoring Flow", () => {
  it("renders live per-endpoint request counts and latency metrics", () => {
    const mockTelemetry: AdapterTelemetryRecord[] = [
      {
        platform: "youtube",
        endpoint: "channels.list",
        total_calls: 150,
        error_count: 2,
        avg_latency_ms: 124.5,
      },
      {
        platform: "x",
        endpoint: "/2/users/by/username",
        total_calls: 85,
        error_count: 0,
        avg_latency_ms: 98.2,
      },
    ];

    render(<AdapterTelemetryTable telemetry={mockTelemetry} />);
    expect(screen.getByText("channels.list")).toBeInTheDocument();
    expect(screen.getByText("124.5 ms")).toBeInTheDocument();
    expect(screen.getByText("/2/users/by/username")).toBeInTheDocument();
    expect(screen.getByText("98.2 ms")).toBeInTheDocument();
  });
});
