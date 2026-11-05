import React from "react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../ui/table";
import type { AccountFeature } from "../../lib/api/types";

export interface AccountFeaturesTableProps {
  features: AccountFeature[];
}

export function AccountFeaturesTable({ features }: AccountFeaturesTableProps) {
  if (features.length === 0) {
    return (
      <div className="py-8 text-center text-xs text-muted-foreground bg-white/5 rounded-lg">
        No feature extractions available for this account.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/5 bg-slate-900/40 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Feature Name</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Observed Value</TableHead>
            <TableHead>Availability</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {features.map((f, idx) => (
            <TableRow key={idx}>
              <TableCell className="font-mono text-xs font-semibold text-foreground">
                {f.feature_name}
              </TableCell>
              <TableCell className="text-xs text-muted-foreground capitalize">
                {f.category}
              </TableCell>
              <TableCell className="font-mono text-xs text-foreground">
                {f.value !== null && f.value !== undefined ? f.value.toFixed(4) : "—"}
              </TableCell>
              <TableCell>
                <span className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                  f.is_available
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : "bg-slate-500/10 text-slate-400 border border-slate-500/20"
                }`}>
                  {f.is_available ? "Available" : f.unavailable_reason || "Unavailable"}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
