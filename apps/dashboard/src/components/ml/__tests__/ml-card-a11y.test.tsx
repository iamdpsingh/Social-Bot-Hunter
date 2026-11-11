import { render } from '@testing-library/react';
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
