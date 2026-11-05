import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ClusterIndicator } from "../../../components/investigation/cluster-indicator";

describe("Scenario: Botnet Cluster Indicator Display", () => {
  it("renders cluster badge with account count or standalone fallback", () => {
    const { rerender } = render(<ClusterIndicator clusterId="cls_farm_8819" clusterSize={35} />);
    expect(screen.getByText("Cluster #8819")).toBeInTheDocument();
    expect(screen.getByText("35 accts")).toBeInTheDocument();

    rerender(<ClusterIndicator />);
    expect(screen.getByText("Standalone")).toBeInTheDocument();
  });
});
