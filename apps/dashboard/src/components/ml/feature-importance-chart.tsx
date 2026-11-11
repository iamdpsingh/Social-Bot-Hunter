'use client';

import React from 'react';

interface FeatureImportanceChartProps {
  importances: Record<string, number>;
  maxItems?: number;
}

export function FeatureImportanceChart({ importances, maxItems = 8 }: FeatureImportanceChartProps) {
  const sortedPairs = Object.entries(importances)
    .sort(([, a], [, b]) => b - a)
    .slice(0, maxItems);

  const maxVal = sortedPairs[0] ? sortedPairs[0][1] : 1.0;

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm" data-testid="feature-importance-chart">
      <div className="border-b border-border pb-4">
        <h3 className="text-base font-semibold text-foreground">Global Feature Importance (Gini Impurity)</h3>
        <p className="text-xs text-muted-foreground mt-0.5">
          Top predictive indicators distinguishing automated bots from organic accounts
        </p>
      </div>

      <div className="mt-6 space-y-3">
        {sortedPairs.map(([name, val]) => {
          const pct = Math.round((val / (maxVal || 1)) * 100);
          const isMissingIndicator = name.startsWith('is_missing_');
          const cleanName = name.replace('is_missing_', '[missing] ');

          return (
            <div key={name} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className={`font-mono ${isMissingIndicator ? 'text-amber-500' : 'text-foreground'}`}>
                  {cleanName}
                </span>
                <span className="font-semibold text-muted-foreground">{(val * 100).toFixed(1)}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    isMissingIndicator ? 'bg-amber-500' : 'bg-primary'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
