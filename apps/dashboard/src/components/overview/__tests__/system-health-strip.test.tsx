import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SystemHealthStrip } from "../system-health-strip";

vi.mock("../../../lib/hooks/use-health", () => ({
  useHealth: () => ({
    health: {
      status: "ok",
      version: "0.1.0",
      database: "connected",
      timestamp: "2026-11-04T12:00:00Z",
    },
    isLoading: false,
    isError: false,
  }),
}));

describe("SystemHealthStrip component", () => {
  it("renders active health signals across system components", () => {
    render(<SystemHealthStrip />);
    expect(screen.getByText("API Status:")).toBeInTheDocument();
    expect(screen.getByText("Operational")).toBeInTheDocument();
    expect(screen.getByText("Database Backend:")).toBeInTheDocument();
    expect(screen.getByText("Worker Engine:")).toBeInTheDocument();
  });
});
