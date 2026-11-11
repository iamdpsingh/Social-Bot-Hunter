import { render, screen } from '@testing-library/react';
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
