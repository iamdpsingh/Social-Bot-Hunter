import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SynchronizedBurstTimeline } from "../synchronized-burst-timeline";

describe("SynchronizedBurstTimeline", () => {
  it("renders empty state when bursts list is empty", () => {
    render(<SynchronizedBurstTimeline bursts={[]} />);
    expect(screen.getByTestId("burst-timeline-empty")).toBeInTheDocument();
  });

  it("renders bursts list with lift multipliers", () => {
    const bursts = [
      {
        burst_id: "burst_001",
        start_timestamp: 1000,
        end_timestamp: 1060,
        post_count: 12,
        participating_accounts: ["u1", "u2"],
        coordination_lift: 3.5,
      },
    ];
    render(<SynchronizedBurstTimeline bursts={bursts} />);
    expect(screen.getByTestId("synchronized-burst-timeline")).toBeInTheDocument();
    expect(screen.getByText("3.5x Lift")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });
});
