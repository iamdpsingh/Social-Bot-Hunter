import React from 'react';
import type { StorageStats } from '@/lib/types/runtime';

interface StorageBreakdownCardProps {
  stats: StorageStats;
  onPrune?: () => void;
  pruning?: boolean;
}

export function StorageBreakdownCard({ stats, onPrune, pruning }: StorageBreakdownCardProps) {
  const categories = Object.values(stats.categories);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg" data-testid="storage-breakdown-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Local Filesystem Storage</h3>
          <p className="text-xs text-slate-400">
            Total Allocated: <strong className="text-slate-200">{stats.total_mb.toFixed(2)} MB</strong> ({stats.total_files} files)
          </p>
        </div>
        {onPrune && (
          <button
            onClick={onPrune}
            disabled={pruning}
            className="px-3 py-1 text-xs font-medium text-amber-400 bg-amber-500/10 border border-amber-500/30 rounded hover:bg-amber-500/20 transition disabled:opacity-50"
          >
            {pruning ? 'Pruning...' : 'Run Retention Sweep'}
          </button>
        )}
      </div>

      <div className="space-y-3">
        {categories.map((c) => {
          const pct = stats.total_mb > 0 ? (c.total_mb / stats.total_mb) * 100 : 0;
          return (
            <div key={c.category} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="font-medium text-slate-300 capitalize">{c.category}</span>
                <span className="text-slate-400 font-mono">
                  {c.file_count} files | {c.total_mb.toFixed(2)} MB ({pct.toFixed(0)}%)
                </span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, Math.max(2, pct))}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
