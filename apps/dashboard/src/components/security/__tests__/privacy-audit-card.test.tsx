import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { PrivacyAuditCard } from '../privacy-audit-card';
import { PrivacyScanResponse } from '../../../lib/types/security';

const mockPrivacy: PrivacyScanResponse = {
  passed: true,
  total_findings: 0,
  scanned_sources: 12,
  findings: [],
};

describe('PrivacyAuditCard', () => {
  it('renders privacy audit sources count and zero findings alert', () => {
    render(<PrivacyAuditCard privacy={mockPrivacy} />);
    expect(screen.getByText('Privacy & PII Audit')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });
});
