import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountNeighborhoodViewer } from "../account-neighborhood-viewer";

describe("AccountNeighborhoodViewer component", () => {
  it("renders inbound and outbound lists", () => {
    const inEdges = [{ source: "user_a", target: "self", relationship_type: "follower" }];
    const outEdges = [{ source: "self", target: "user_b", relationship_type: "following" }];
    render(<AccountNeighborhoodViewer inEdges={inEdges} outEdges={outEdges} />);
    expect(screen.getByText("Inbound Followers")).toBeInTheDocument();
    expect(screen.getByText("Outbound Following")).toBeInTheDocument();
    expect(screen.getByText("user_a")).toBeInTheDocument();
    expect(screen.getByText("user_b")).toBeInTheDocument();
  });
});
