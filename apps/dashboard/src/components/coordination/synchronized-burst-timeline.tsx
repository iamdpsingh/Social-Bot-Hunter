"use client";

import React from "react";
import type { TemporalBurstItem } from "../../lib/api/types";

interface SynchronizedBurstTimelineProps {
  bursts: TemporalBurstItem[];
}

export function SynchronizedBurstTimeline({ bursts }: SynchronizedBurstTimelineProps) {
  if (!bursts || bursts.length === 0) {
    return (
      <div
        data-testid="burst-timeline-empty"
        className="p-8 text-center rounded-xl border border-dashed border-border bg-card/50 text-muted-foreground"
      >
        <p className="text-sm">No abnormal synchronized posting bursts detected in this investigation scan.</p>
      </div>
    );
  }

  return (
    <div data-testid="synchronized-burst-timeline" className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
          <span>Synchronized Posting Bursts</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 border border-red-500/20">
            {bursts.length} Events Detected
          </span>
        </h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {bursts.map((burst) => (
          <div
            key={burst.burst_id}
            data-testid={`burst-item-${burst.burst_id}`}
            className="p-4 rounded-lg border border-border bg-card text-card-foreground shadow-sm"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs font-semibold text-primary">{burst.burst_id}</span>
              <span className="text-xs font-bold text-red-500 bg-red-500/10 px-2 py-0.5 rounded">
                {burst.coordination_lift}x Lift
              </span>
            </div>
            <div className="space-y-1 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Total Posts in Window:</span>
                <span className="font-semibold text-foreground">{burst.post_count}</span>
              </div>
              <div className="flex justify-between">
                <span>Participating Accounts:</span>
                <span className="font-semibold text-foreground">{burst.participating_accounts.length}</span>
              </div>
            </div>
            <div className="mt-3 pt-2 border-t border-border/50">
              <span className="text-[11px] text-muted-foreground">Synchronized Accounts:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {burst.participating_accounts.map((acc) => (
                  <span key={acc} className="text-[10px] px-1.5 py-0.5 bg-muted rounded font-mono">
                    @{acc}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
