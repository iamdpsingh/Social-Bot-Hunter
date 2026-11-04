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
      components: {
        api: "healthy",
        database: "connected",
        worker_pool: "4 active workers",
      },
    },
    isLoading: false,
  }),
}));

describe("SystemHealthStrip component", () => {
  it("renders active health signals across system components", () => {
    render(<SystemHealthStrip />);
    expect(screen.getByText("API Gateway")).toBeInTheDocument();
    expect(screen.getByText("Database (Postgres)")).toBeInTheDocument();
    expect(screen.getByText("Worker Pool")).toBeInTheDocument();
    expect(screen.getByText("4 active workers")).toBeInTheDocument();
  });
});
