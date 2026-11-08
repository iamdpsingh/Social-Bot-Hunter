"use client";

import React from "react";
import { AdapterTelemetryRecord } from "../../lib/api/types";
import { cn } from "../../lib/utils";

interface AdapterTelemetryTableProps {
  telemetry: AdapterTelemetryRecord[];
  className?: string;
}

export function AdapterTelemetryTable({ telemetry, className }: AdapterTelemetryTableProps) {
  if (!telemetry || telemetry.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-muted-foreground border border-dashed border-white/10 rounded-xl">
        No adapter telemetry recorded yet. Calls will register here in real-time.
      </div>
    );
  }

  return (
    <div className={cn("overflow-hidden rounded-xl border border-white/10 bg-card/60 shadow-lg", className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-muted-foreground">
          <thead className="bg-white/5 text-[11px] uppercase tracking-wider text-muted-foreground/80 border-b border-white/10">
            <tr>
              <th scope="col" className="px-4 py-3 font-semibold">Platform</th>
              <th scope="col" className="px-4 py-3 font-semibold">Endpoint</th>
              <th scope="col" className="px-4 py-3 font-semibold text-right">Total Calls</th>
              <th scope="col" className="px-4 py-3 font-semibold text-right">Errors</th>
              <th scope="col" className="px-4 py-3 font-semibold text-right">Avg Latency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono">
            {telemetry.map((t, idx) => (
              <tr key={`${t.platform}-${t.endpoint}-${idx}`} className="hover:bg-white/5 transition-colors">
                <td className="px-4 py-2.5 font-sans capitalize font-medium text-foreground">
                  {t.platform}
                </td>
                <td className="px-4 py-2.5 text-foreground">{t.endpoint}</td>
                <td className="px-4 py-2.5 text-right font-semibold text-foreground">
                  {t.total_calls.toLocaleString()}
                </td>
                <td className="px-4 py-2.5 text-right">
                  <span className={cn(t.error_count > 0 ? "text-rose-400 font-semibold" : "text-muted-foreground")}>
                    {t.error_count}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right text-foreground">
                  {t.avg_latency_ms.toFixed(1)} ms
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
