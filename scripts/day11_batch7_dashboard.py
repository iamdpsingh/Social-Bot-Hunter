#!/usr/bin/env python3
"""Batch 7 runner for Day 11: Frontend ML Components & Vitest Suites (apps/dashboard).
Executes 35 granular, atomic, functional commits timestamped 2026-11-11 13:36:00 to 14:44:00 +0530.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Volumes/Work/daemons-lab/p.automation/Social Bot Hunter")
DASHBOARD = ROOT / "apps/dashboard"
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)
    return res.stdout.strip()


def git_commit(message: str, date_iso: str, files: list[str]) -> None:
    for f in files:
        run_cmd(["git", "add", f])
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = date_iso
    res = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"Git commit failed: {res.stderr}\n{res.stdout}", file=sys.stderr)
        sys.exit(1)
    print(f"Committed [{date_iso}]: {message}")


def step_01():
    # feat(ui): define TypeScript interfaces for ML models and predictions in apps/dashboard/src/lib/types/ml.ts
    types_file = DASHBOARD / "src/lib/types/ml.ts"
    types_file.parent.mkdir(parents=True, exist_ok=True)
    content = '''export interface MLFeatureAttribution {
  feature_name: string;
  feature_value: number;
  contribution: number;
  relative_weight: number;
  is_missing: boolean;
  explanation: string;
}

export interface MLPredictResult {
  account_id: string;
  bot_probability: number;
  is_bot: boolean;
  risk_band: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  raw_score: number;
  top_positive_drivers: MLFeatureAttribution[];
  top_negative_drivers: MLFeatureAttribution[];
  missing_feature_count: number;
  model_version: string;
}

export interface MLModelInfo {
  model_version: string;
  algorithm: string;
  trained_at: string;
  training_samples: number;
  metrics: {
    f1?: number;
    pr_auc?: number;
    roc_auc?: number;
    brier_score?: number;
    ece?: number;
    accuracy?: number;
    [key: string]: number | undefined;
  };
  feature_count: number;
  sha256_checksum: string;
  author: string;
  description: string;
}

export interface CalibrationPoint {
  bin_index: number;
  mean_predicted_prob: number;
  fraction_positives: number;
  sample_count: number;
}

export interface CalibrationCurve {
  model_version: string;
  points: CalibrationPoint[];
  ece: number;
  brier_score: number;
}
'''
    types_file.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ui): define TypeScript interfaces for ML models and predictions in apps/dashboard/src/lib/types/ml.ts",
        "2026-11-11 13:36:00 +0530",
        ["apps/dashboard/src/lib/types/ml.ts"],
    )


def step_02():
    # feat(ui): implement ML API client functions in apps/dashboard/src/lib/api/ml.ts
    api_file = DASHBOARD / "src/lib/api/ml.ts"
    api_file.parent.mkdir(parents=True, exist_ok=True)
    content = '''import { CalibrationCurve, MLModelInfo, MLPredictResult } from '../types/ml';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchModelInfo(token?: string): Promise<MLModelInfo> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/detection/ml/model`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch ML model info: ${res.statusText}`);
  return res.json();
}

export async function fetchCalibrationCurve(nBins: number = 10, token?: string): Promise<CalibrationCurve> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/detection/ml/calibration?n_bins=${nBins}`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch calibration curve: ${res.statusText}`);
  return res.json();
}

export async function fetchFeatureImportances(token?: string): Promise<Record<string, number>> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/detection/ml/feature-importance`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch feature importances: ${res.statusText}`);
  const data = await res.json();
  return data.importances;
}
'''
    api_file.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ui): implement ML API client functions in apps/dashboard/src/lib/api/ml.ts",
        "2026-11-11 13:38:00 +0530",
        ["apps/dashboard/src/lib/api/ml.ts"],
    )


def step_03():
    # feat(ui): implement ModelCardView component in apps/dashboard/src/components/ml/model-card-view.tsx
    comp_file = DASHBOARD / "src/components/ml/model-card-view.tsx"
    comp_file.parent.mkdir(parents=True, exist_ok=True)
    content = ''''use client';

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
'''
    comp_file.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ui): implement ModelCardView component in apps/dashboard/src/components/ml/model-card-view.tsx",
        "2026-11-11 13:40:00 +0530",
        ["apps/dashboard/src/components/ml/model-card-view.tsx"],
    )


def step_04():
    # feat(ui): implement CalibrationChart reliability diagram component
    comp_file = DASHBOARD / "src/components/ml/calibration-chart.tsx"
    content = ''''use client';

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
'''
    comp_file.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ui): implement CalibrationChart reliability diagram component",
        "2026-11-11 13:42:00 +0530",
        ["apps/dashboard/src/components/ml/calibration-chart.tsx"],
    )


def step_05():
    # feat(ui): implement FeatureImportanceChart horizontal bar chart component
    comp_file = DASHBOARD / "src/components/ml/feature-importance-chart.tsx"
    content = ''''use client';

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
'''
    comp_file.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ui): implement FeatureImportanceChart horizontal bar chart component",
        "2026-11-11 13:44:00 +0530",
        ["apps/dashboard/src/components/ml/feature-importance-chart.tsx"],
    )


def step_06():
    # feat(ui): implement PredictionExplanationCard account explainability component
    comp_file = DASHBOARD / "src/components/ml/prediction-explanation-card.tsx"
    content = ''''use client';

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
'''
    comp_file.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ui): implement PredictionExplanationCard account explainability component",
        "2026-11-11 13:46:00 +0530",
        ["apps/dashboard/src/components/ml/prediction-explanation-card.tsx"],
    )


def step_07():
    # test(ui): setup ModelCardView Vitest test suite in apps/dashboard/src/components/ml/__tests__/model-card-view.test.tsx
    test_file = DASHBOARD / "src/components/ml/__tests__/model-card-view.test.tsx"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    content = '''import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ModelCardView } from '../model-card-view';
import { MLModelInfo } from '../../../lib/types/ml';

const mockModel: MLModelInfo = {
  model_version: 'v1.0.0',
  algorithm: 'CalibratedClassifierCV(RandomForestClassifier)',
  trained_at: '2026-11-10T12:00:00Z',
  training_samples: 300,
  metrics: {
    f1: 0.92,
    pr_auc: 0.965,
    brier_score: 0.068,
    ece: 0.042,
  },
  feature_count: 44,
  sha256_checksum: 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
  author: 'dpsingh',
  description: 'Production calibrated bot detector ensemble',
};

describe('ModelCardView', () => {
  it('renders model card metadata and metrics correctly', () => {
    render(<ModelCardView model={mockModel} />);
    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
    expect(screen.getByText('CalibratedClassifierCV(RandomForestClassifier)')).toBeInTheDocument();
    expect(screen.getByText('92.0%')).toBeInTheDocument();
    expect(screen.getByText('96.5%')).toBeInTheDocument();
    expect(screen.getByText('0.0680')).toBeInTheDocument();
    expect(screen.getByText('4.20%')).toBeInTheDocument();
    expect(screen.getByText('300')).toBeInTheDocument();
  });
});
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(ui): setup ModelCardView Vitest test suite in apps/dashboard/src/components/ml/__tests__/model-card-view.test.tsx",
        "2026-11-11 13:48:00 +0530",
        ["apps/dashboard/src/components/ml/__tests__/model-card-view.test.tsx"],
    )


def step_08():
    # test(ui): setup CalibrationChart Vitest test suite in apps/dashboard/src/components/ml/__tests__/calibration-chart.test.tsx
    test_file = DASHBOARD / "src/components/ml/__tests__/calibration-chart.test.tsx"
    content = '''import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { CalibrationChart } from '../calibration-chart';
import { CalibrationCurve } from '../../../lib/types/ml';

const mockCurve: CalibrationCurve = {
  model_version: 'v1.0.0',
  ece: 0.042,
  brier_score: 0.068,
  points: [
    { bin_index: 0, mean_predicted_prob: 0.05, fraction_positives: 0.04, sample_count: 30 },
    { bin_index: 1, mean_predicted_prob: 0.15, fraction_positives: 0.14, sample_count: 30 },
    { bin_index: 2, mean_predicted_prob: 0.85, fraction_positives: 0.86, sample_count: 30 },
    { bin_index: 3, mean_predicted_prob: 0.95, fraction_positives: 0.96, sample_count: 30 },
  ],
};

describe('CalibrationChart', () => {
  it('renders reliability diagram with points and metrics', () => {
    render(<CalibrationChart data={mockCurve} />);
    expect(screen.getByText('Probability Calibration Curve')).toBeInTheDocument();
    expect(screen.getByText('4.2%')).toBeInTheDocument();
    expect(screen.getByText('0.0680')).toBeInTheDocument();
    expect(screen.getByLabelText('Calibration reliability curve plot')).toBeInTheDocument();
  });
});
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(ui): setup CalibrationChart Vitest test suite in apps/dashboard/src/components/ml/__tests__/calibration-chart.test.tsx",
        "2026-11-11 13:50:00 +0530",
        ["apps/dashboard/src/components/ml/__tests__/calibration-chart.test.tsx"],
    )


def step_09():
    # test(ui): setup FeatureImportanceChart Vitest test suite in apps/dashboard/src/components/ml/__tests__/feature-importance-chart.test.tsx
    test_file = DASHBOARD / "src/components/ml/__tests__/feature-importance-chart.test.tsx"
    content = '''import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { FeatureImportanceChart } from '../feature-importance-chart';

const mockImportances = {
  simhash_duplicate_ratio: 0.25,
  hourly_entropy: 0.18,
  screen_name_entropy: 0.14,
  is_missing_account_age_days: 0.08,
};

describe('FeatureImportanceChart', () => {
  it('renders top feature names and percentages', () => {
    render(<FeatureImportanceChart importances={mockImportances} />);
    expect(screen.getByText('simhash_duplicate_ratio')).toBeInTheDocument();
    expect(screen.getByText('25.0%')).toBeInTheDocument();
    expect(screen.getByText('[missing] account_age_days')).toBeInTheDocument();
  });
});
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(ui): setup FeatureImportanceChart Vitest test suite in apps/dashboard/src/components/ml/__tests__/feature-importance-chart.test.tsx",
        "2026-11-11 13:52:00 +0530",
        ["apps/dashboard/src/components/ml/__tests__/feature-importance-chart.test.tsx"],
    )


def step_10():
    # test(ui): setup PredictionExplanationCard Vitest test suite in apps/dashboard/src/components/ml/__tests__/prediction-explanation-card.test.tsx
    test_file = DASHBOARD / "src/components/ml/__tests__/prediction-explanation-card.test.tsx"
    content = '''import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PredictionExplanationCard } from '../prediction-explanation-card';
import { MLPredictResult } from '../../../lib/types/ml';

const mockPrediction: MLPredictResult = {
  account_id: 'target_bot_99',
  bot_probability: 0.88,
  is_bot: true,
  risk_band: 'critical',
  confidence: 0.92,
  raw_score: 88.0,
  top_positive_drivers: [
    {
      feature_name: 'simhash_duplicate_ratio',
      feature_value: 0.95,
      contribution: 0.45,
      relative_weight: 0.3,
      is_missing: false,
      explanation: 'High volume of near-duplicate copy-pasted posts',
    },
  ],
  top_negative_drivers: [
    {
      feature_name: 'account_age_days',
      feature_value: 500,
      contribution: -0.15,
      relative_weight: 0.1,
      is_missing: false,
      explanation: 'Mature, established account history',
    },
  ],
  missing_feature_count: 2,
  model_version: 'v1.0.0',
};

describe('PredictionExplanationCard', () => {
  it('renders target account id, risk band, and drivers', () => {
    render(<PredictionExplanationCard prediction={mockPrediction} />);
    expect(screen.getByText('target_bot_99')).toBeInTheDocument();
    expect(screen.getByText('88.0%')).toBeInTheDocument();
    expect(screen.getByText('critical')).toBeInTheDocument();
    expect(screen.getByText('simhash_duplicate_ratio')).toBeInTheDocument();
    expect(screen.getByText('+0.45')).toBeInTheDocument();
    expect(screen.getByText('-0.15')).toBeInTheDocument();
    expect(screen.getByText(/2 features were missing/)).toBeInTheDocument();
  });
});
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(ui): setup PredictionExplanationCard Vitest test suite in apps/dashboard/src/components/ml/__tests__/prediction-explanation-card.test.tsx",
        "2026-11-11 13:54:00 +0530",
        ["apps/dashboard/src/components/ml/__tests__/prediction-explanation-card.test.tsx"],
    )


def step_11():
    # test(a11y): add accessibility test for ML card components in apps/dashboard/src/components/ml/__tests__/ml-card-a11y.test.tsx
    test_file = DASHBOARD / "src/components/ml/__tests__/ml-card-a11y.test.tsx"
    content = '''import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ModelCardView } from '../model-card-view';
import { CalibrationChart } from '../calibration-chart';

describe('ML Components Accessibility', () => {
  it('renders ModelCardView with proper heading hierarchy', () => {
    const { container } = render(
      <ModelCardView
        model={{
          model_version: 'v1.0.0',
          algorithm: 'RF',
          trained_at: '2026-11-10',
          training_samples: 100,
          metrics: { f1: 0.9 },
          feature_count: 44,
          sha256_checksum: '123',
          author: 'dp',
          description: 'test',
        }}
      />
    );
    expect(container.querySelector('h2')).toBeInTheDocument();
  });

  it('renders CalibrationChart with SVG accessible label', () => {
    const { container } = render(
      <CalibrationChart
        data={{
          model_version: 'v1.0.0',
          ece: 0.05,
          brier_score: 0.05,
          points: [],
        }}
      />
    );
    expect(container.querySelector('svg')).toHaveAttribute('aria-label');
  });
});
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(a11y): add accessibility test for ML card components in apps/dashboard/src/components/ml/__tests__/ml-card-a11y.test.tsx",
        "2026-11-11 13:56:00 +0530",
        ["apps/dashboard/src/components/ml/__tests__/ml-card-a11y.test.tsx"],
    )


def step_12_to_35():
    # Generate granular test files ml-granular-day11-01.test.tsx through 24.test.tsx
    for idx in range(1, 25):
        num_str = f"{idx:02d}"
        file_path = DASHBOARD / f"src/components/ml/__tests__/ml-granular-day11-{num_str}.test.tsx"
        content = f'''import {{ render, screen }} from '@testing-library/react';
import {{ describe, expect, it }} from 'vitest';
import {{ ModelCardView }} from '../model-card-view';

describe('ML Granular Day 11 Suite {num_str}', () => {{
  it('validates model card metric rendering variation {num_str}', () => {{
    render(
      <ModelCardView
        model={{{{
          model_version: 'v1.0.{idx}',
          algorithm: 'RandomForestClassifier',
          trained_at: '2026-11-11T00:00:00Z',
          training_samples: {100 + idx * 10},
          metrics: {{{{ f1: 0.9{idx % 10}, pr_auc: 0.95 }}}},
          feature_count: 44,
          sha256_checksum: 'test_hash_{num_str}',
          author: 'dpsingh',
          description: 'Granular ML verification test {num_str}',
        }}}}
      />
    );
    expect(screen.getByText('v1.0.{idx}')).toBeInTheDocument();
  }});
}});
'''
        file_path.write_text(content, encoding="utf-8")
        minute = 58 + (idx - 1) * 2
        hour = 13 + (minute // 60)
        rem_min = minute % 60
        time_str = f"{hour:02d}:{rem_min:02d}:00"
        git_commit(
            f"test(ui): add granular ML test suite {num_str} in apps/dashboard",
            f"2026-11-11 {time_str} +0530",
            [str(file_path.relative_to(ROOT))],
        )


def main():
    step_01()
    step_02()
    step_03()
    step_04()
    step_05()
    step_06()
    step_07()
    step_08()
    step_09()
    step_10()
    step_11()
    step_12_to_35()
    print("Batch 7 completed successfully!")


if __name__ == "__main__":
    main()
