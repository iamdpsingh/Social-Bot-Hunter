import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ModelCardView } from '../model-card-view';

describe('ML Granular Day 11 Suite 07', () => {
  it('validates model card metric rendering variation 07', () => {
    render(
      <ModelCardView
        model={{
          model_version: 'v1.0.7',
          algorithm: 'RandomForestClassifier',
          trained_at: '2026-11-11T00:00:00Z',
          training_samples: 170,
          metrics: { f1: 0.97, pr_auc: 0.95 },
          feature_count: 44,
          sha256_checksum: 'test_hash_07',
          author: 'dpsingh',
          description: 'Granular ML verification test 07',
        }}
      />
    );
    expect(screen.getByText('v1.0.7')).toBeInTheDocument();
  });
});
