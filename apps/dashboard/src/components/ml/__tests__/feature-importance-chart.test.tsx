import { render, screen } from '@testing-library/react';
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
