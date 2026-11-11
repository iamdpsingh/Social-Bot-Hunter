'use client';

import React from 'react';
import { MLModelInfo } from '../../lib/types/ml';

interface ModelCardViewProps {
  model: MLModelInfo;
}

export function ModelCardView({ model }: ModelCardViewProps) {
  const m = model.metrics || {};

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm" data-testid="model-card-view">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold tracking-tight text-foreground">
              {model.model_version}
            </h2>
            <span className="inline-flex items-center rounded-md bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-500 border border-emerald-500/20">
              Active Production
            </span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{model.description}</p>
        </div>
        <div className="flex flex-col sm:items-end">
          <span className="text-xs text-muted-foreground">Algorithm</span>
          <code className="text-xs font-mono font-medium text-foreground bg-muted px-2 py-0.5 rounded">
            {model.algorithm}
          </code>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-lg bg-muted/50 p-3">
          <span className="text-xs text-muted-foreground block">F1-Score</span>
          <span className="text-lg font-bold text-foreground">
            {m.f1 !== undefined ? (m.f1 * 100).toFixed(1) + '%' : 'N/A'}
          </span>
        </div>
        <div className="rounded-lg bg-muted/50 p-3">
          <span className="text-xs text-muted-foreground block">PR-AUC</span>
          <span className="text-lg font-bold text-foreground">
            {m.pr_auc !== undefined ? (m.pr_auc * 100).toFixed(1) + '%' : 'N/A'}
          </span>
        </div>
        <div className="rounded-lg bg-muted/50 p-3">
          <span className="text-xs text-muted-foreground block">Brier Score</span>
          <span className="text-lg font-bold text-foreground">
            {m.brier_score !== undefined ? m.brier_score.toFixed(4) : 'N/A'}
          </span>
        </div>
        <div className="rounded-lg bg-muted/50 p-3">
          <span className="text-xs text-muted-foreground block">Expected Cal. Error</span>
          <span className="text-lg font-bold text-foreground">
            {m.ece !== undefined ? (m.ece * 100).toFixed(2) + '%' : 'N/A'}
          </span>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between text-xs text-muted-foreground pt-4 border-t border-border gap-2">
        <div>
          <span>Trained on </span>
          <strong className="text-foreground">{model.training_samples.toLocaleString()}</strong>
          <span> samples ({model.feature_count} features)</span>
        </div>
        <div className="flex items-center gap-1">
          <span>SHA-256: </span>
          <code className="font-mono text-muted-foreground/80" title={model.sha256_checksum}>
            {model.sha256_checksum.slice(0, 12)}...
          </code>
        </div>
      </div>
    </div>
  );
}
