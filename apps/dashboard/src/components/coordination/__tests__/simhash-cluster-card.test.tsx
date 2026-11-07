import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SimHashClusterCard } from "../simhash-cluster-card";

describe("SimHashClusterCard", () => {
  const mockCluster = {
    cluster_id: "cluster_001",
    representative_text: "Vote for proposition A today!",
    member_count: 5,
    account_ids: ["acc1", "acc2"],
    sample_texts: ["Vote for proposition A today!", "Vote for proposition A urgent!"],
    avg_pairwise_similarity: 0.95,
    max_hamming_distance: 2,
  };

  it("renders cluster details correctly", () => {
    render(<SimHashClusterCard cluster={mockCluster} scanId="s1" />);
    expect(screen.getByTestId("simhash-cluster-cluster_001")).toBeInTheDocument();
    expect(screen.getByText("5 Accounts")).toBeInTheDocument();
    expect(screen.getByText("95% Match")).toBeInTheDocument();
    expect(screen.getByText(/Vote for proposition A today!/)).toBeInTheDocument();
  });

  it("toggles expandable variation samples", () => {
    render(<SimHashClusterCard cluster={mockCluster} scanId="s1" />);
    const toggle = screen.getByTestId("toggle-samples-cluster_001");
    fireEvent.click(toggle);
    expect(screen.getByText("Sample Variations:")).toBeInTheDocument();
    expect(screen.getByText(/Vote for proposition A urgent!/)).toBeInTheDocument();
  });
});
