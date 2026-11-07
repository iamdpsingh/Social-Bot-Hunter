"use client";

import React, { useState } from "react";
import type { RetentionStatsResponse } from "../../lib/api/types";

interface RetentionConfigCardProps {
  stats: RetentionStatsResponse | null;
  onPurge: (days: number, dryRun: boolean) => Promise<void>;
}

export function RetentionConfigCard({ stats, onPurge }: RetentionConfigCardProps) {
  const [retentionDays, setRetentionDays] = useState(90);
  const [purging, setPurging] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handlePurgeClick = async (dryRun: boolean) => {
    try {
      setPurging(true);
      setStatusMsg(null);
      await onPurge(retentionDays, dryRun);
      setStatusMsg(dryRun ? "Dry run complete: verified purge candidates" : "Data retention purge executed successfully");
    } catch {
      setStatusMsg("Purge operation failed");
    } finally {
      setPurging(false);
    }
  };

  return (
    <div data-testid="retention-config-card" className="p-6 rounded-2xl border border-border bg-card shadow-sm space-y-5">
      <div>
        <h3 className="text-base font-bold text-foreground">Data Retention & Privacy Lifecycle</h3>
        <p className="text-xs text-muted-foreground mt-0.5">
          Configure time-to-live policies to automatically purge expired raw evidence and investigation snapshots.
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-3 rounded-lg bg-muted/40 border border-border">
            <span className="text-[11px] text-muted-foreground uppercase font-semibold">Total Scans Stored</span>
            <span className="block text-xl font-bold text-foreground mt-1">{stats.total_scans}</span>
          </div>
          <div className="p-3 rounded-lg bg-muted/40 border border-border">
            <span className="text-[11px] text-muted-foreground uppercase font-semibold">Expired Scans Pending</span>
            <span className="block text-xl font-bold text-amber-500 mt-1">{stats.expired_scans_count}</span>
          </div>
          <div className="p-3 rounded-lg bg-muted/40 border border-border">
            <span className="text-[11px] text-muted-foreground uppercase font-semibold">Storage Footprint</span>
            <span className="block text-xl font-bold text-foreground mt-1">
              {Math.round(stats.database_size_bytes / 1024)} KB
            </span>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-3 border-t border-border">
        <label className="text-xs font-semibold text-muted-foreground flex items-center gap-2">
          <span>Retention Window:</span>
          <select
            value={retentionDays}
            onChange={(e) => setRetentionDays(Number(e.target.value))}
            className="px-2.5 py-1.5 rounded-lg border border-border bg-background text-foreground text-xs"
          >
            <option value={30}>30 Days (Strict Privacy)</option>
            <option value={60}>60 Days</option>
            <option value={90}>90 Days (Default)</option>
            <option value={180}>180 Days (Long-Term Audit)</option>
          </select>
        </label>

        <div className="flex items-center gap-2">
          <button
            type="button"
            data-testid="btn-dry-run-purge"
            disabled={purging}
            onClick={() => handlePurgeClick(true)}
            className="px-4 py-2 rounded-lg border border-border bg-background text-foreground text-xs font-semibold hover:bg-muted transition-colors disabled:opacity-50"
          >
            Dry Run
          </button>
          <button
            type="button"
            data-testid="btn-execute-purge"
            disabled={purging}
            onClick={() => handlePurgeClick(false)}
            className="px-4 py-2 rounded-lg bg-destructive text-destructive-foreground text-xs font-semibold hover:bg-destructive/90 transition-colors disabled:opacity-50"
          >
            Purge Expired Data
          </button>
        </div>
      </div>

      {statusMsg && (
        <div data-testid="retention-status-msg" className="text-xs font-medium text-emerald-500 bg-emerald-500/10 p-2.5 rounded border border-emerald-500/20">
          {statusMsg}
        </div>
      )}
    </div>
  );
}
