import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import NotFound from "../not-found";

describe("NotFound page", () => {
  it("renders 404 header and return to overview link", () => {
    render(<NotFound />);
    expect(screen.getByText("404")).toBeInTheDocument();
    expect(screen.getByText("Investigation Not Found")).toBeInTheDocument();
    expect(screen.getByText("Return to Overview")).toBeInTheDocument();
  });
});
