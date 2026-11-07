import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { CoordinationClient } from "../../../../app/investigations/[id]/coordination/coordination-client";
import * as coordinationHook from "../../../../lib/hooks/use-coordination";

describe("Scenario: Coordination Detection Workflow", () => {
  it("allows analyst to inspect content clusters and view sample messages", () => {
    vi.spyOn(coordinationHook, "useCoordination").mockReturnValue({
      coordination: {
        scan_id: "scan_test_1",
        simhash_clusters: [
          {
            cluster_id: "cluster_crypto_airdrop",
            representative_text: "Urgent: claim your $500 crypto bonus at link",
            member_count: 6,
            account_ids: ["bot1", "bot2"],
            sample_texts: [
              "Urgent: claim your $500 crypto bonus at link",
              "Urgent: claim your $500 crypto bonus at link today",
            ],
            avg_pairwise_similarity: 0.94,
            max_hamming_distance: 3,
          },
        ],
        temporal_bursts: [
          {
            burst_id: "burst_001",
            start_timestamp: 100,
            end_timestamp: 150,
            post_count: 8,
            participating_accounts: ["bot1", "bot2"],
            coordination_lift: 4.2,
          },
        ],
        shared_hubs: [
          {
            target_id: "target_account",
            target_handle: "CryptoLeader",
            shared_by_count: 5,
            follower_account_ids: ["bot1", "bot2"],
            jaccard_overlap: 0.85,
          },
        ],
        total_coordinated_accounts: 6,
        overall_coordination_score: 0.88,
      },
      isLoading: false,
      isError: false,
      error: null,
      mutate: vi.fn(),
    });

    render(<CoordinationClient scanId="scan_test_1" />);

    expect(screen.getByTestId("coordination-overview-banner")).toHaveTextContent("88%");
    expect(screen.getByTestId("simhash-cluster-cluster_crypto_airdrop")).toBeInTheDocument();

    const toggleBtn = screen.getByTestId("toggle-samples-cluster_crypto_airdrop");
    fireEvent.click(toggleBtn);
    expect(screen.getByText(/claim your \$500 crypto bonus at link today/)).toBeInTheDocument();
  });
});
