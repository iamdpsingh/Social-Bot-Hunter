import React from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../ui/table";
import { RiskBadge } from "../ui/badge";
import { PlatformIcon } from "../ui/platform-icon";
import type { AccountAssessment } from "../../lib/api/types";
import type { Platform } from "../../lib/api/types";

export interface RelationshipTableProps {
  scanId: string;
  accounts: AccountAssessment[];
  platform?: Platform;
  isLoading?: boolean;
}

export function RelationshipTable({
  scanId,
  accounts,
  platform = "x",
  isLoading = false,
}: RelationshipTableProps) {
  if (isLoading) {
    return (
      <div className="py-12 text-center text-xs text-muted-foreground animate-pulse">
        Loading relationship explorer records...
      </div>
    );
  }

  if (accounts.length === 0) {
    return (
      <div className="py-12 text-center text-xs text-muted-foreground">
        No matching accounts found for current filter criteria.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/5 bg-slate-900/40 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Account / Handle</TableHead>
            <TableHead>Risk Level</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Evidence Coverage</TableHead>
            <TableHead>Available Signals</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {accounts.map((acc) => {
            const username = acc.username || acc.platform_account_id;
            return (
              <TableRow key={acc.id || acc.platform_account_id}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <PlatformIcon platform={platform} size={14} />
                    <div>
                      <span className="font-semibold text-foreground text-xs block">
                        @{username}
                      </span>
                      <span className="font-mono text-[10px] text-muted-foreground">
                        {acc.platform_account_id}
                      </span>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <RiskBadge score={acc.score} band={acc.band ?? undefined} />
                </TableCell>
                <TableCell>
                  <span className="font-mono text-xs font-bold text-foreground">
                    {acc.score !== null && acc.score !== undefined ? `${Math.round(acc.score * 100)}%` : "N/A"}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="font-mono text-xs text-muted-foreground">
                    {Math.round((acc.evidence_coverage ?? 1.0) * 100)}%
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-muted-foreground">
                    {acc.features_available ?? 0} / {acc.features_total ?? 0}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <Link
                    href={`/investigations/${scanId}/accounts/${acc.platform_account_id}`}
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-medium"
                  >
                    Inspect <ArrowUpRight className="h-3 w-3" />
                  </Link>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
