"use client";

import React, { useState } from "react";
import { useCoordination } from "../../../../lib/hooks/use-coordination";
import { CoordinationOverviewBanner } from "../../../../components/coordination/coordination-overview-banner";
import { SimHashClusterCard } from "../../../../components/coordination/simhash-cluster-card";
import { SynchronizedBurstTimeline } from "../../../../components/coordination/synchronized-burst-timeline";
import { SharedHubMatrix } from "../../../../components/coordination/shared-hub-matrix";
import { InvestigationTabs, type TabType } from "../../../../components/investigation/investigation-tabs";

interface CoordinationClientProps {
  scanId: string;
}

export function CoordinationClient({ scanId }: CoordinationClientProps) {
  const [activeTab, setActiveTab] = useState<TabType>("coordination");
  const [burstWindow, setBurstWindow] = useState(60);
  const [minDist, setMinDist] = useState(4);
  const { coordination, isLoading, isError, mutate } = useCoordination(scanId, burstWindow, minDist);

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    if (tab === "overview") window.location.href = `/investigations/${scanId}`;
    else if (tab === "network") window.location.href = `/investigations/${scanId}/graph`;
    else if (tab !== "coordination") window.location.href = `/investigations/${scanId}#${tab}`;
  };

  if (isLoading) {
    return (
      <div data-testid="coordination-loading" className="p-12 text-center text-sm text-muted-foreground animate-pulse">
        Analyzing coordinated activity across message content and temporal graph...
      </div>
    );
  }

  if (isError || !coordination) {
    return (
      <div data-testid="coordination-error" className="p-8 text-center rounded-xl border border-destructive/30 bg-destructive/10 text-destructive">
        <p className="font-semibold">Failed to load coordination analysis</p>
        <button
          type="button"
          onClick={() => mutate()}
          className="mt-3 text-xs px-3 py-1.5 rounded bg-destructive text-destructive-foreground font-medium"
        >
          Retry Analysis
        </button>
      </div>
    );
  }

  return (
    <div data-testid="coordination-page-client" className="space-y-8">
      <InvestigationTabs activeTab={activeTab} onTabChange={handleTabChange} />

      <CoordinationOverviewBanner coordination={coordination} />

      {/* Filter and threshold controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl border border-border bg-card">
        <div className="flex items-center gap-4">
          <label className="text-xs font-medium text-muted-foreground flex items-center gap-2">
            <span>Burst Window:</span>
            <select
              value={burstWindow}
              onChange={(e) => setBurstWindow(Number(e.target.value))}
              className="text-xs px-2 py-1 rounded border border-border bg-background text-foreground"
            >
              <option value={30}>30 Seconds</option>
              <option value={60}>60 Seconds</option>
              <option value={300}>5 Minutes</option>
              <option value={900}>15 Minutes</option>
            </select>
          </label>

          <label className="text-xs font-medium text-muted-foreground flex items-center gap-2">
            <span>Text Match Threshold:</span>
            <select
              value={minDist}
              onChange={(e) => setMinDist(Number(e.target.value))}
              className="text-xs px-2 py-1 rounded border border-border bg-background text-foreground"
            >
              <option value={2}>Strict (&le; 2 bits)</option>
              <option value={4}>Standard (&le; 4 bits)</option>
              <option value={8}>Relaxed (&le; 8 bits)</option>
              <option value={12}>Broad (&le; 12 bits)</option>
            </select>
          </label>
        </div>

        <span className="text-xs text-muted-foreground">
          Showing {coordination.simhash_clusters.length} Content Clusters &bull; {coordination.temporal_bursts.length} Bursts
        </span>
      </div>

      {/* Content Clusters */}
      <section className="space-y-4">
        <h4 className="text-base font-bold text-foreground">
          Repeated Content Clusters ({coordination.simhash_clusters.length})
        </h4>
        {coordination.simhash_clusters.length === 0 ? (
          <p className="text-xs text-muted-foreground italic">No repeated text clusters found.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {coordination.simhash_clusters.map((c) => (
              <SimHashClusterCard key={c.cluster_id} cluster={c} scanId={scanId} />
            ))}
          </div>
        )}
      </section>

      {/* Synchronized Temporal Bursts */}
      <section>
        <SynchronizedBurstTimeline bursts={coordination.temporal_bursts} />
      </section>

      {/* Shared Target Hubs */}
      <section>
        <SharedHubMatrix hubs={coordination.shared_hubs} />
      </section>
    </div>
  );
}
