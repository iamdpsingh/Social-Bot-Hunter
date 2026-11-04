# Frontend Unit and Scenario Testing Guide

## Testing Framework
- **Test Runner**: Vitest with `@testing-library/react` and `jsdom`.
- **Coverage**:
  - UI Component Primitives (Button, Badge, Modal, Card, Table, Alert, Input, Select, Tooltip).
  - Layout & Overview Shell (Header, Sidebar, AppShell, SystemHealthStrip, RecentScansTable).
  - State & Hooks (useHealth, useScans, useCapabilities, useAudit, useScanEvents).
  - Utility and Formatters (formatRelativeTime, formatNumber, scoreToRiskBand, convertToCsv).
  - Accessibility & WCAG Compliance.
  - End-to-End User Scenarios (Scan launch flow, live event stream, synthetic data detection).

## Execution
```bash
cd apps/dashboard
npm run test
```
