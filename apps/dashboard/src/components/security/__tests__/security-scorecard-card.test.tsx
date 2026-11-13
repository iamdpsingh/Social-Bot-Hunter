import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { SecurityScorecardCard } from '../security-scorecard-card';
import { SecurityScorecardResponse } from '../../../lib/types/security';

const mockScorecard: SecurityScorecardResponse = {
  passed_audit: true,
  total_checks: 3,
  passed_checks: 3,
  failed_checks: 0,
  findings: [],
  checks: [
    {
      category: 'secrets',
      check_id: 'SEC-CREDS-01',
      name: 'Hardcoded credentials scan',
      passed: true,
      findings_count: 0,
      details: {},
    },
  ],
};

describe('SecurityScorecardCard', () => {
  it('renders overall passing score and grade', () => {
    render(<SecurityScorecardCard scorecard={mockScorecard} />);
    expect(screen.getByText('Security Audit Scorecard')).toBeInTheDocument();
    expect(screen.getByText('Grade A')).toBeInTheDocument();
    expect(screen.getByText('Hardcoded credentials scan')).toBeInTheDocument();
  });
});
