import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TimelineSnapshot } from "../timeline-snapshot";

describe("TimelineSnapshot component", () => {
  it("renders observed timestamp and snapshot stats", () => {
    render(
      <TimelineSnapshot
        observedAt="2026-11-05T09:00:00Z"
        source="official_api"
        followers={1500}
        following={800}
      />
    );
    expect(screen.getByText("Snapshot Observed")).toBeInTheDocument();
    expect(screen.getByText("1,500 followers")).toBeInTheDocument();
    expect(screen.getByText("official_api")).toBeInTheDocument();
  });
});
