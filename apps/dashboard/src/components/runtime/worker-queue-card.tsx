import React from 'react';
import type { WorkerJob } from '@/lib/types/runtime';

interface WorkerQueueCardProps {
  jobs: WorkerJob[];
  queueStats: Record<string, number>;
  onEnqueueJob?: (taskType: string) => void;
}

export function WorkerQueueCard({ jobs, queueStats, onEnqueueJob }: WorkerQueueCardProps) {
  const getStatusBadge = (st: string) => {
    switch (st) {
      case 'completed':
        return <span className="px-2 py-0.5 text-xs rounded bg-emerald-500/20 text-emerald-400">Done</span>;
      case 'running':
        return <span className="px-2 py-0.5 text-xs rounded bg-sky-500/20 text-sky-400 animate-pulse">Running</span>;
      case 'failed':
      case 'dead_letter':
        return <span className="px-2 py-0.5 text-xs rounded bg-rose-500/20 text-rose-400">Failed</span>;
      default:
        return <span className="px-2 py-0.5 text-xs rounded bg-amber-500/20 text-amber-400">Queued</span>;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg" data-testid="worker-queue-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Local Background Worker Queue</h3>
          <p className="text-xs text-slate-400">SQLite FIFO Dispatcher with Lease Management</p>
        </div>
        <div className="flex gap-2">
          {onEnqueueJob && (
            <button
              onClick={() => onEnqueueJob('storage.prune')}
              className="px-2.5 py-1 text-xs font-medium text-sky-400 bg-sky-500/10 border border-sky-500/30 rounded hover:bg-sky-500/20 transition"
            >
              + Prune Job
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 mb-4">
        <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/50 text-center">
          <div className="text-xs text-slate-400">Queued</div>
          <div className="text-lg font-bold text-amber-400">{queueStats['queued'] ?? 0}</div>
        </div>
        <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/50 text-center">
          <div className="text-xs text-slate-400">Running</div>
          <div className="text-lg font-bold text-sky-400">{queueStats['running'] ?? 0}</div>
        </div>
        <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/50 text-center">
          <div className="text-xs text-slate-400">Completed</div>
          <div className="text-lg font-bold text-emerald-400">{queueStats['completed'] ?? 0}</div>
        </div>
        <div className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/50 text-center">
          <div className="text-xs text-slate-400">Dead Letter</div>
          <div className="text-lg font-bold text-rose-400">{queueStats['dead_letter'] ?? 0}</div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/70 text-slate-400 uppercase">
            <tr>
              <th className="p-2">Task</th>
              <th className="p-2">Status</th>
              <th className="p-2">Priority</th>
              <th className="p-2">Attempts</th>
              <th className="p-2">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-4 text-center text-slate-500">No jobs in queue history</td>
              </tr>
            ) : (
              jobs.slice(0, 5).map((job) => (
                <tr key={job.job_id} className="hover:bg-slate-800/40">
                  <td className="p-2 font-mono">{job.task_type}</td>
                  <td className="p-2">{getStatusBadge(job.status)}</td>
                  <td className="p-2">{job.priority}</td>
                  <td className="p-2">{job.attempts} / {job.max_attempts}</td>
                  <td className="p-2 text-slate-400">{new Date(job.created_at).toLocaleTimeString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
