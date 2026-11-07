"use client";

import React, { useState } from "react";
import type { AccountDiffItem } from "../../lib/api/types";

interface DiffAccountTableProps {
  accounts: AccountDiffItem[];
}

export function DiffAccountTable({ accounts }: DiffAccountTableProps) {
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState<string>("");

  const filtered = accounts.filter((acc) => {
    if (filter !== "all" && acc.status !== filter) return false;
    if (search && !acc.handle.toLowerCase().includes(search.toLowerCase()) && !acc.account_id.includes(search)) {
      return false;
    }
    return true;
  });

  return (
    <div data-testid="diff-account-table" className="space-y-4 rounded-xl border border-border bg-card p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Filter tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {[
            { id: "all", label: "All Differences" },
            { id: "confirmed_added", label: "Confirmed Added" },
            { id: "confirmed_removed", label: "Confirmed Removed" },
            { id: "persisting", label: "Persisting Accounts" },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              data-testid={`filter-tab-${tab.id}`}
              onClick={() => setFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                filter === tab.id
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <input
          type="text"
          data-testid="input-table-search"
          placeholder="Filter by handle or ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 text-xs rounded-lg border border-border bg-background text-foreground w-full sm:w-60 focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-muted/50 border-b border-border">
              <th className="p-3 font-semibold text-muted-foreground">Account</th>
              <th className="p-3 font-semibold text-muted-foreground">Change Status</th>
              <th className="p-3 font-semibold text-muted-foreground">Baseline Risk</th>
              <th className="p-3 font-semibold text-muted-foreground">Comparison Risk</th>
              <th className="p-3 font-semibold text-muted-foreground">Provenance & Notes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-6 text-center text-muted-foreground italic">
                  No accounts matching current filter criteria.
                </td>
              </tr>
            ) : (
              filtered.map((acc) => (
                <tr key={acc.account_id} data-testid={`row-${acc.account_id}`} className="hover:bg-muted/30">
                  <td className="p-3 font-mono font-medium text-foreground">
                    <div>
                      <span>@{acc.handle}</span>
                      <span className="block text-[10px] text-muted-foreground font-normal">{acc.account_id}</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        acc.status === "confirmed_added"
                          ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                          : acc.status === "confirmed_removed"
                          ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                          : "bg-blue-500/10 text-blue-500 border border-blue-500/20"
                      }`}
                    >
                      {acc.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="p-3">
                    {acc.risk_score_a !== null && acc.risk_score_a !== undefined ? (
                      <span className="font-mono text-xs">{Math.round(acc.risk_score_a * 100)}% ({acc.risk_band_a})</span>
                    ) : (
                      <span className="text-muted-foreground italic text-[11px]">&mdash;</span>
                    )}
                  </td>
                  <td className="p-3">
                    {acc.risk_score_b !== null && acc.risk_score_b !== undefined ? (
                      <span className="font-mono text-xs">{Math.round(acc.risk_score_b * 100)}% ({acc.risk_band_b})</span>
                    ) : (
                      <span className="text-muted-foreground italic text-[11px]">&mdash;</span>
                    )}
                  </td>
                  <td className="p-3 text-muted-foreground text-[11px]">
                    {acc.provenance_note}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
