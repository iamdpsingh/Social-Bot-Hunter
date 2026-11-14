import React from 'react';
import { Gauge, CheckCircle2, XCircle } from 'lucide-react';
import { BenchmarkSlaEntry } from '../../lib/types/acceptance';

interface Props {
  entries: BenchmarkSlaEntry[];
}

export function LatencyBenchmarkTable({ entries }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 pb-4 border-b border-border">
        <Gauge className="h-6 w-6 text-primary" />
        <div>
          <h2 className="text-lg font-bold text-foreground">Latency Benchmarks & SLAs</h2>
          <p className="text-xs text-muted-foreground">Micro-benchmark percentile performance verification</p>
        </div>
      </div>

      <div className="overflow-x-auto mt-4">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs text-muted-foreground">
              <th className="pb-2">Task</th>
              <th className="pb-2">p50 (ms)</th>
              <th className="pb-2">p90 (ms)</th>
              <th className="pb-2">p99 (ms)</th>
              <th className="pb-2">SLA Limit</th>
              <th className="pb-2 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {entries.map((e) => (
              <tr key={e.taskName} className="text-foreground">
                <td className="py-2.5 font-mono text-xs">{e.taskName}</td>
                <td className="py-2.5 text-xs">{e.p50Ms.toFixed(3)}</td>
                <td className="py-2.5 text-xs">{e.p90Ms.toFixed(3)}</td>
                <td className="py-2.5 text-xs font-semibold">{e.p99Ms.toFixed(3)}</td>
                <td className="py-2.5 text-xs text-muted-foreground">&le; {e.slaLimitMs} ms</td>
                <td className="py-2.5 text-right">
                  {e.passedSla ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-500">
                      <CheckCircle2 className="h-3.5 w-3.5" /> PASS
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-500">
                      <XCircle className="h-3.5 w-3.5" /> FAIL
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
