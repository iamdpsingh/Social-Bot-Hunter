import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ModelCardView } from '../model-card-view';

describe('ML Granular Day 11 Suite 01', () => {
  it('validates model card metric rendering variation 01', () => {
    render(
      <ModelCardView
        model={{
          model_version: 'v1.0.1',
          algorithm: 'RandomForestClassifier',
          trained_at: '2026-11-11T00:00:00Z',
          training_samples: 110,
          metrics: { f1: 0.91, pr_auc: 0.95 },
          feature_count: 44,
          sha256_checksum: 'test_hash_01',
          author: 'dpsingh',
          description: 'Granular ML verification test 01',
        }}
      />
    );
    expect(screen.getByText('v1.0.1')).toBeInTheDocument();
  });
});
