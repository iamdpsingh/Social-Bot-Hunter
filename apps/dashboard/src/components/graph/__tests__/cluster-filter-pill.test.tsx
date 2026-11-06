import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { ClusterFilterPill } from "../cluster-filter-pill";

describe("ClusterFilterPill component", () => {
  it("renders cluster pill and dispatches onClear callback", () => {
    const onClear = vi.fn();
    render(<ClusterFilterPill clusterId="cluster_99" onClear={onClear} />);

    expect(screen.getByText("Cluster: cluster_99")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Remove cluster filter" }));
    expect(onClear).toHaveBeenCalledTimes(1);
  });
});
