import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../table";

describe("Table component", () => {
  it("renders structured table elements", () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Target</TableHead>
            <TableHead>Platform</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>@alex_hunter</TableCell>
            <TableCell>X</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );

    expect(screen.getByText("Target")).toBeInTheDocument();
    expect(screen.getByText("Platform")).toBeInTheDocument();
    expect(screen.getByText("@alex_hunter")).toBeInTheDocument();
  });
});
