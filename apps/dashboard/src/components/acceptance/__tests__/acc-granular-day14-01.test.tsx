import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { ReadinessScorecard } from '../readiness-scorecard';

describe('AccGranularDay1401', () => {
  it('renders 100% badge', () => {
    render(
      <ReadinessScorecard
        scorecard={{
          compliancePercentage: 100,
          totalCriteria: 1,
          verifiedCriteria: 1,
          overallStatus: 'PRODUCTION_READY',
          evaluatedAt: '2026-11-14',
          criteria: [],
        }}
      />
    );
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});
