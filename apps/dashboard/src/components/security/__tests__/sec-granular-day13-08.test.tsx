import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { PrivacyAuditCard } from '../privacy-audit-card';

describe('GranularSecurityDay13_08', () => {
  it('renders privacy card case 08', () => {
    render(
      <PrivacyAuditCard
        privacy={{
          passed: true,
          total_findings: 0,
          scanned_sources: 8,
          findings: [],
        }}
      />
    );
    expect(screen.getByText('8')).toBeInTheDocument();
  });
});
