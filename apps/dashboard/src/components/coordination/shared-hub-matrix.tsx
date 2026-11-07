"use client";

import React from "react";
import type { SharedHubItem } from "../../lib/api/types";

interface SharedHubMatrixProps {
  hubs: SharedHubItem[];
}

export function SharedHubMatrix({ hubs }: SharedHubMatrixProps) {
  if (!hubs || hubs.length === 0) {
    return (
      <div
        data-testid="shared-hub-empty"
        className="p-8 text-center rounded-xl border border-dashed border-border bg-card/50 text-muted-foreground"
      >
        <p className="text-sm">No shared target follow hubs identified in this network.</p>
      </div>
    );
  }

  return (
    <div data-testid="shared-hub-matrix" className="space-y-4">
      <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
        <span>Shared Follow Targets & Influencer Hubs</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 border border-blue-500/20">
          {hubs.length} Hubs
        </span>
      </h4>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-muted/50 border-b border-border">
              <th className="p-3 font-semibold text-muted-foreground">Target Account</th>
              <th className="p-3 font-semibold text-muted-foreground">Shared By Bots</th>
              <th className="p-3 font-semibold text-muted-foreground">Network Overlap</th>
              <th className="p-3 font-semibold text-muted-foreground">Follower Accounts</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {hubs.map((hub) => (
              <tr key={hub.target_id} data-testid={`hub-row-${hub.target_id}`} className="hover:bg-muted/30">
                <td className="p-3 font-medium text-foreground">
                  <div>
                    <span className="font-mono text-primary">@{hub.target_handle}</span>
                    <span className="block text-[10px] text-muted-foreground">{hub.target_id}</span>
                  </div>
                </td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded-full font-bold bg-muted text-foreground">
                    {hub.shared_by_count}
                  </span>
                </td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${Math.round(hub.jaccard_overlap * 100)}%` }}
                      />
                    </div>
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {Math.round(hub.jaccard_overlap * 100)}%
                    </span>
                  </div>
                </td>
                <td className="p-3">
                  <div className="flex flex-wrap gap-1 max-w-md">
                    {hub.follower_account_ids.slice(0, 5).map((f) => (
                      <span key={f} className="text-[10px] px-1.5 py-0.5 rounded bg-muted font-mono">
                        @{f}
                      </span>
                    ))}
                    {hub.follower_account_ids.length > 5 && (
                      <span className="text-[10px] text-muted-foreground self-center">
                        +{hub.follower_account_ids.length - 5} more
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
