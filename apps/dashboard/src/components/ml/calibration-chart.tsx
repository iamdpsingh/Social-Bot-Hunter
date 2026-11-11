'use client';

import React from 'react';
import { CalibrationCurve } from '../../lib/types/ml';

interface CalibrationChartProps {
  data: CalibrationCurve;
}

export function CalibrationChart({ data }: CalibrationChartProps) {
  const points = data.points || [];

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm" data-testid="calibration-chart">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h3 className="text-base font-semibold text-foreground">Probability Calibration Curve</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Reliability diagram: observed empirical positive rate vs predicted probability
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-muted-foreground">
            ECE: <strong className="text-foreground">{(data.ece * 100).toFixed(1)}%</strong>
          </span>
          <span className="text-muted-foreground">
            Brier: <strong className="text-foreground">{data.brier_score.toFixed(4)}</strong>
          </span>
        </div>
      </div>

      <div className="mt-6 flex justify-center">
        <svg
          viewBox="0 0 300 200"
          className="w-full max-w-md h-48 overflow-visible"
          aria-label="Calibration reliability curve plot"
        >
          {/* Grid lines */}
          <line x1="30" y1="170" x2="280" y2="170" stroke="currentColor" className="text-border" strokeWidth="1" />
          <line x1="30" y1="20" x2="30" y2="170" stroke="currentColor" className="text-border" strokeWidth="1" />

          {/* Perfect diagonal reference (dashed) */}
          <line
            x1="30"
            y1="170"
            x2="280"
            y2="20"
            stroke="currentColor"
            className="text-muted-foreground/40"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />

          {/* Calibration Curve line */}
          <polyline
            fill="none"
            stroke="#10b981"
            strokeWidth="2.5"
            points={points
              .map((p) => {
                const x = 30 + p.mean_predicted_prob * 250;
                const y = 170 - p.fraction_positives * 150;
                return `${x},${y}`;
              })
              .join(' ')}
          />

          {/* Points */}
          {points.map((p, idx) => {
            const cx = 30 + p.mean_predicted_prob * 250;
            const cy = 170 - p.fraction_positives * 150;
            return (
              <circle
                key={idx}
                cx={cx}
                cy={cy}
                r="4"
                className="fill-emerald-500 hover:fill-emerald-400 cursor-pointer transition-colors"
              >
                <title>{`Bin ${p.bin_index + 1}: Pred ${(p.mean_predicted_prob * 100).toFixed(0)}%, True ${(p.fraction_positives * 100).toFixed(0)}%`}</title>
              </circle>
            );
          })}

          {/* Labels */}
          <text x="30" y="190" className="text-[10px] fill-muted-foreground">0%</text>
          <text x="150" y="190" className="text-[10px] fill-muted-foreground" textAnchor="middle">Predicted Probability</text>
          <text x="280" y="190" className="text-[10px] fill-muted-foreground" textAnchor="end">100%</text>
        </svg>
      </div>

      <div className="mt-4 flex items-center justify-center gap-6 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-muted-foreground/40 inline-block border-t border-dashed" />
          <span>Perfect Calibration</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-emerald-500 inline-block" />
          <span>Calibrated Bot Classifier</span>
        </div>
      </div>
    </div>
  );
}
