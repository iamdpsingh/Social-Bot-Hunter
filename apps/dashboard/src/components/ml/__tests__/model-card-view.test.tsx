import { render, screen } from '@testing-library/react';
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
