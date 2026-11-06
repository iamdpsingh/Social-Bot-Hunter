import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphBreadcrumbs } from "../graph-breadcrumbs";

describe("GraphBreadcrumbs component", () => {
  it("renders breadcrumbs trail including active focal node", () => {
    render(<GraphBreadcrumbs scanId="s_99" activeNodeId="focal_node_1" />);
    expect(screen.getByText("Investigations")).toBeInTheDocument();
    expect(screen.getByText("s_99")).toBeInTheDocument();
    expect(screen.getByText("Network Explorer")).toBeInTheDocument();
    expect(screen.getByText("focal_node_1")).toBeInTheDocument();
  });
});
