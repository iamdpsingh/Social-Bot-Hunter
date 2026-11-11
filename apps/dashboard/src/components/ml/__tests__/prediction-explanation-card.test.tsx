import { render, screen } from '@testing-library/react';
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
