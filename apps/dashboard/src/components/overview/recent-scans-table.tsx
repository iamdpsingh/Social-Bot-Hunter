"use client";

import React from "react";
import Link from "next/link";
import { RefreshCw, XCircle, ArrowRight, ExternalLink } from "lucide-react";
import { useScans } from "../../lib/hooks/use-scans";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { ScanStatusBadge } from "../ui/badge";
import { PlatformIcon } from "../ui/platform-icon";
import { Button } from "../ui/button";
import { Skeleton } from "../ui/skeleton";
import { EmptyInvestigationState } from "./empty-investigation-state";

export function RecentScansTable({ onNewScan }: { onNewScan?: () => void }) {
  const { scans, isLoading, cancelScan, retryScan } = useScans(10);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-72 mt-1" />
        </CardHeader>
        <CardContent className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (scans.length === 0) {
    return <EmptyInvestigationState onActionClick={onNewScan} />;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <div>
          <CardTitle>Recent Investigations</CardTitle>
          <CardDescription>Live status, execution progress, and data provenance</CardDescription>
        </div>
        <Link href="/history" className="text-xs text-primary hover:underline flex items-center gap-1">
          View all scans <ArrowRight className="h-3 w-3" />
        </Link>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">Platform</TableHead>
              <TableHead>Scan Identifier</TableHead>
              <TableHead>Origin / Mode</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {scans.map((scan) => (
              <TableRow key={scan.id}>
                <TableCell>
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-foreground border border-white/5">
                    <PlatformIcon platform={scan.platform} size={15} />
                  </div>
                </TableCell>
                <TableCell>
                  <div className="font-mono text-xs font-semibold text-foreground flex items-center gap-2">
                    <span>{scan.id.substring(0, 8)}...</span>
                    <span className="text-[10px] text-muted-foreground font-normal bg-white/5 px-1.5 py-0.5 rounded">
                      {scan.requested_by}
                    </span>
                  </div>
                  {scan.failure_reason && (
                    <p className="text-[11px] text-red-400 mt-0.5 truncate max-w-xs">{scan.failure_reason}</p>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex flex-col text-xs">
                    <span className="capitalize font-medium text-slate-300">
                      {scan.collection_mode.replace("_", " ")}
                    </span>
                    <span className="text-[10px] text-muted-foreground uppercase font-mono">
                      {scan.data_origin}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <ScanStatusBadge status={scan.status} />
                </TableCell>
                <TableCell className="text-xs text-muted-foreground font-mono">
                  {new Date(scan.created_at).toLocaleDateString()} {new Date(scan.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    {scan.status === "running" && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => cancelScan(scan.id)}
                        className="h-7 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        title="Cancel active scan"
                      >
                        <XCircle className="h-3.5 w-3.5 mr-1" /> Cancel
                      </Button>
                    )}
                    {(scan.status === "failed" || scan.status === "cancelled") && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => retryScan(scan.id)}
                        className="h-7 text-xs text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                        title="Retry from last checkpoint"
                      >
                        <RefreshCw className="h-3.5 w-3.5 mr-1" /> Retry
                      </Button>
                    )}
                    <Link
                      href={`/investigations/${scan.id}`}
                      className="inline-flex items-center justify-center h-7 px-2.5 rounded text-xs font-medium bg-white/5 text-foreground hover:bg-white/10 transition-colors"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
