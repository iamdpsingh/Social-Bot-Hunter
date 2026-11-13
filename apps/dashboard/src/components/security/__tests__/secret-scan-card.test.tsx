import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { SecretScanCard } from '../secret-scan-card';
import { SecretScanResponse } from '../../../lib/types/security';

const mockScan: SecretScanResponse = {
  target_dir: '/repo/root',
  total_findings: 0,
  findings: [],
  passed: true,
};

describe('SecretScanCard', () => {
  it('renders clean scan state when zero secrets found', () => {
    render(<SecretScanCard scan={mockScan} />);
    expect(screen.getByText('Hardcoded Secret Scanner')).toBeInTheDocument();
    expect(screen.getByText('Zero hardcoded secrets detected')).toBeInTheDocument();
  });
});
