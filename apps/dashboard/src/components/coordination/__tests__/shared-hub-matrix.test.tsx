import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SharedHubMatrix } from "../shared-hub-matrix";

describe("SharedHubMatrix", () => {
  it("renders empty state when hubs list is empty", () => {
    render(<SharedHubMatrix hubs={[]} />);
    expect(screen.getByTestId("shared-hub-empty")).toBeInTheDocument();
  });

  it("renders hubs table with target handles and overlap percentage", () => {
    const hubs = [
      {
        target_id: "tgt_1",
        target_handle: "MainHub",
        shared_by_count: 8,
        follower_account_ids: ["acc1", "acc2"],
        jaccard_overlap: 0.75,
      },
    ];
    render(<SharedHubMatrix hubs={hubs} />);
    expect(screen.getByTestId("shared-hub-matrix")).toBeInTheDocument();
    expect(screen.getByText("@MainHub")).toBeInTheDocument();
    expect(screen.getByText("75%")).toBeInTheDocument();
  });
});
