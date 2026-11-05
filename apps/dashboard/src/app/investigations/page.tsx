"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Plus, ShieldCheck, ArrowRight, Activity } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { useScans } from "../../lib/hooks/use-scans";
import { LaunchScanModal } from "../../components/overview/launch-scan-modal";
import { SyntheticDataBanner } from "../../components/ui/synthetic-banner";

export default function InvestigationsPage() {
  const { scans, isLoading, isError } = useScans();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredScans = (scans || []).filter((s) => {
    const targetName = (s as any).target || s.requested_by || "";
    const matchSearch =
      targetName.toLowerCase().includes(search.toLowerCase()) ||
      s.id.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "ALL" || s.status.toUpperCase() === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6 pb-12" data-testid="investigations-page">
      <SyntheticDataBanner />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-foreground">Investigation Archives</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Search, filter, and inspect past and active social network bot scans.
          </p>
        </div>

        <Button onClick={() => setIsModalOpen(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          New Investigation
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by target or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        <div className="flex gap-1.5 self-start sm:self-auto">
          {["ALL", "COMPLETED", "RUNNING", "FAILED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                statusFilter === st
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted/40 text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-xs text-muted-foreground">Loading investigations...</div>
        ) : filteredScans.length === 0 ? (
          <div className="p-8 text-center space-y-2">
            <ShieldCheck className="h-8 w-8 text-muted-foreground mx-auto" />
            <div className="text-sm font-medium text-foreground">No investigations found</div>
            <div className="text-xs text-muted-foreground">Try clearing your search query or start a new scan.</div>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {filteredScans.map((scan) => (
              <div
                key={scan.id}
                className="p-4 flex items-center justify-between hover:bg-muted/20 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm text-foreground">{(scan as any).target || scan.requested_by}</span>
                    <Badge variant={scan.status === "complete" ? "success" : "secondary"}>
                      {scan.status}
                    </Badge>
                    <span className="text-xs font-mono text-muted-foreground">{scan.platform}</span>
                  </div>
                  <div className="text-xs text-muted-foreground flex items-center gap-3">
                    <span>ID: {scan.id}</span>
                    <span>•</span>
                    <span>Created: {new Date(scan.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <Link
                  href={`/investigations/${scan.id}`}
                  className="flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
                >
                  Inspect
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      <LaunchScanModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
