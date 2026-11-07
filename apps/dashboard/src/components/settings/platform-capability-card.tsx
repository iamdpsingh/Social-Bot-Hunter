"use client";

import React from "react";
import type { PlatformQuotaStatus } from "../../lib/api/types";

interface PlatformCapabilityCardProps {
  quotas: PlatformQuotaStatus[];
}

export function PlatformCapabilityCard({ quotas }: PlatformCapabilityCardProps) {
  return (
    <div data-testid="platform-capability-card" className="p-6 rounded-2xl border border-border bg-card shadow-sm space-y-4">
      <div>
        <h3 className="text-base font-bold text-foreground">Platform Capabilities & Quotas</h3>
        <p className="text-xs text-muted-foreground mt-0.5">
          Official API access status, rate limit thresholds, and daily quota consumption pools.
        </p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-muted/50 border-b border-border">
              <th className="p-3 font-semibold text-muted-foreground">Platform</th>
              <th className="p-3 font-semibold text-muted-foreground">Auth State</th>
              <th className="p-3 font-semibold text-muted-foreground">Status</th>
              <th className="p-3 font-semibold text-muted-foreground">Daily Quota Pool</th>
              <th className="p-3 font-semibold text-muted-foreground">Rate Limit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {quotas.map((q) => (
              <tr key={q.platform} data-testid={`quota-row-${q.platform}`} className="hover:bg-muted/30">
                <td className="p-3 font-semibold uppercase text-foreground">{q.platform}</td>
                <td className="p-3">
                  <span className="font-mono text-[11px] text-muted-foreground">{q.auth_state}</span>
                </td>
                <td className="p-3">
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      q.status === "active"
                        ? "bg-emerald-500/10 text-emerald-500"
                        : q.status === "limited"
                        ? "bg-amber-500/10 text-amber-500"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {q.status}
                  </span>
                </td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs">{q.quota_remaining.toLocaleString()} left</span>
                    <span className="text-[10px] text-muted-foreground">/ {q.daily_quota_limit.toLocaleString()}</span>
                  </div>
                </td>
                <td className="p-3 font-mono text-xs">{q.rate_limit_rpm} req/min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
