"use client";

import React, { useState } from "react";
import type { SimHashClusterItem } from "../../lib/api/types";

interface SimHashClusterCardProps {
  cluster: SimHashClusterItem;
  scanId: string;
}

export function SimHashClusterCard({ cluster, scanId }: SimHashClusterCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      data-testid={`simhash-cluster-${cluster.cluster_id}`}
      className="p-5 rounded-xl border border-border bg-card text-card-foreground shadow-sm hover:border-primary/50 transition-colors"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground">
              {cluster.cluster_id}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-amber-500/10 text-amber-500 border border-amber-500/20">
              {cluster.member_count} Accounts
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-primary/10 text-primary">
              {Math.round(cluster.avg_pairwise_similarity * 100)}% Match
            </span>
          </div>
          <p className="text-sm font-medium text-foreground mt-2 italic bg-muted/30 p-2.5 rounded border border-border/50">
            "{cluster.representative_text}"
          </p>
        </div>
        <button
          type="button"
          data-testid={`toggle-samples-${cluster.cluster_id}`}
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-primary hover:underline whitespace-nowrap mt-1 font-medium"
        >
          {expanded ? "Hide variations" : `View all (${cluster.sample_texts.length})`}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 pt-3 border-t border-border space-y-2">
          <h5 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Sample Variations:
          </h5>
          <div className="space-y-1.5 pl-2 border-l-2 border-primary/30">
            {cluster.sample_texts.map((txt, idx) => (
              <p key={idx} className="text-xs text-muted-foreground font-mono">
                {idx + 1}. "{txt}"
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        <span className="text-xs text-muted-foreground mr-1">Coordinated Bots:</span>
        {cluster.account_ids.map((accId) => (
          <a
            key={accId}
            href={`/investigations/${encodeURIComponent(scanId)}/accounts/${encodeURIComponent(accId)}`}
            className="text-xs px-2 py-0.5 rounded bg-muted/60 text-foreground hover:bg-primary/20 hover:text-primary transition-colors font-mono"
          >
            @{accId}
          </a>
        ))}
      </div>
    </div>
  );
}
