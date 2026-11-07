import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SimHashClusterCard } from "../../../components/coordination/simhash-cluster-card";

describe("SimHashClusterCard Accessibility", () => {
  const mockCluster = {
    cluster_id: "cluster_test",
    representative_text: "Accessibility test content",
    member_count: 2,
    account_ids: ["acc1", "acc2"],
    sample_texts: ["Accessibility test content"],
    avg_pairwise_similarity: 1.0,
    max_hamming_distance: 0,
  };

  it("provides accessible button controls and readable text", () => {
    render(<SimHashClusterCard cluster={mockCluster} scanId="s1" />);
    const btn = screen.getByRole("button", { name: /View all/i });
    expect(btn).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /@acc1/i })).toHaveAttribute("href");
  });
});
