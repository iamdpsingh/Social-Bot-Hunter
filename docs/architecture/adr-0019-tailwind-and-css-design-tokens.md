# ADR 0019: Tailwind CSS and Custom Design Tokens

## Status
Accepted

## Context
The investigation interface must maintain visual consistency across dark and light modes, provide glassmorphic analytical cards, and enforce high contrast for security analysts working in varied lighting conditions.

## Decision
Configure Tailwind CSS with semantic CSS variables and design tokens in `src/tokens/`. Define explicit color scales for cyber midnight backgrounds and risk tiers.

## Consequences
- Single source of truth for risk colors, typography, and spacing.
- Rapid UI composition with utility classes while preventing arbitrary hex-code drift.
