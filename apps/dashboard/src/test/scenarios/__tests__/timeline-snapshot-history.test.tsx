import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TimelineSnapshot } from "../../../components/investigation/timeline-snapshot";

describe("Scenario: Timeline Snapshot History", () => {
  it("formats follower counts, source, and ISO timestamp cleanly", () => {
    render(
      <TimelineSnapshot
        observedAt="2026-11-05T10:00:00Z"
        source="x_api_v2"
        followers={12500}
        following={340}
      />
    );

    expect(screen.getByText(/12,500 followers/)).toBeInTheDocument();
    expect(screen.getByText(/340 following/)).toBeInTheDocument();
    expect(screen.getByText("x_api_v2")).toBeInTheDocument();
  });
});
