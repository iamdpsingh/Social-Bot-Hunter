import React from 'react';
import type { ProcessInfo, RuntimeStatus } from '@/lib/types/runtime';

interface ProcessSupervisorCardProps {
  status: RuntimeStatus;
  onRefresh?: () => void;
}

export function ProcessSupervisorCard({ status, onRefresh }: ProcessSupervisorCardProps) {
  const services = Object.values(status.services);

  const getStateBadge = (state: string) => {
    switch (state) {
      case 'running':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">RUNNING</span>;
      case 'crashed':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">CRASHED</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-slate-500/20 text-slate-400 border border-slate-500/30">{state.toUpperCase()}</span>;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg" data-testid="process-supervisor-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Local Multi-Service Supervisor</h3>
          <p className="text-xs text-slate-400">PID: {status.supervisor_pid} | Uptime: {status.uptime_seconds}s</p>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="px-3 py-1 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded border border-slate-700 transition"
          >
            Refresh
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        {services.map((svc: ProcessInfo) => (
          <div key={svc.name} className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60">
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium text-sm text-slate-200 capitalize">{svc.name}</span>
              {getStateBadge(svc.state)}
            </div>
            <div className="text-xs text-slate-400 space-y-0.5">
              {svc.port && <div>Port: <span className="text-slate-300 font-mono">{svc.port}</span></div>}
              {svc.pid && <div>PID: <span className="text-slate-300 font-mono">{svc.pid}</span></div>}
              <div>Uptime: <span className="text-slate-300">{svc.uptime_sec}s</span></div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-800">
        <span>CPUs: <strong className="text-slate-200">{status.system.cpu_count} cores</strong></span>
        <span>Memory Usage: <strong className="text-slate-200">{status.system.memory_used_percent}%</strong></span>
      </div>
    </div>
  );
}
