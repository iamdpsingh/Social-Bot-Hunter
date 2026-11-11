'use client';

import React from 'react';
import { MLPredictResult } from '../../lib/types/ml';

interface PredictionExplanationCardProps {
  prediction: MLPredictResult;
}

const BAND_STYLES = {
  critical: 'bg-rose-500/15 text-rose-500 border-rose-500/30',
  high: 'bg-orange-500/15 text-orange-500 border-orange-500/30',
  medium: 'bg-amber-500/15 text-amber-500 border-amber-500/30',
  low: 'bg-emerald-500/15 text-emerald-500 border-emerald-500/30',
};

export function PredictionExplanationCard({ prediction }: PredictionExplanationCardProps) {
  const bandStyle = BAND_STYLES[prediction.risk_band] || BAND_STYLES.low;

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-6" data-testid="prediction-explanation-card">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <span className="text-xs text-muted-foreground">Target Account</span>
          <h3 className="text-lg font-semibold text-foreground">{prediction.account_id}</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-xs text-muted-foreground block">Calibrated Bot Probability</span>
            <span className="text-2xl font-black text-foreground">
              {(prediction.bot_probability * 100).toFixed(1)}%
            </span>
          </div>
          <span className={`inline-flex items-center rounded-lg px-3 py-1.5 text-xs font-bold border uppercase tracking-wider ${bandStyle}`}>
            {prediction.risk_band}
          </span>
        </div>
      </div>

      {prediction.missing_feature_count > 0 && (
        <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3 text-xs text-amber-500 flex items-center gap-2">
          <span className="font-semibold">Evidence Gap:</span>
          <span>{prediction.missing_feature_count} features were missing and safely imputed with zero leakage indicators.</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-xs font-semibold text-rose-500 uppercase tracking-wider mb-3">
            Top Bot Risk Indicators (+)
          </h4>
          <div className="space-y-2">
            {prediction.top_positive_drivers.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">No strong bot indicators observed.</p>
            ) : (
              prediction.top_positive_drivers.map((d, i) => (
                <div key={i} className="rounded-lg bg-muted/40 p-3 border border-border/50 text-xs">
                  <div className="flex items-center justify-between font-mono text-foreground">
                    <span>{d.feature_name}</span>
                    <span className="text-rose-500 font-bold">+{d.contribution.toFixed(2)}</span>
                  </div>
                  <p className="mt-1 text-muted-foreground">{d.explanation}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-emerald-500 uppercase tracking-wider mb-3">
            Top Organic Signals (-)
          </h4>
          <div className="space-y-2">
            {prediction.top_negative_drivers.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">No strong organic signals observed.</p>
            ) : (
              prediction.top_negative_drivers.map((d, i) => (
                <div key={i} className="rounded-lg bg-muted/40 p-3 border border-border/50 text-xs">
                  <div className="flex items-center justify-between font-mono text-foreground">
                    <span>{d.feature_name}</span>
                    <span className="text-emerald-500 font-bold">{d.contribution.toFixed(2)}</span>
                  </div>
                  <p className="mt-1 text-muted-foreground">{d.explanation}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
