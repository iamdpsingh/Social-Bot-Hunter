# ADR-0070: Data Minimization and Ephemeral Social Media Storage Policies

## Status
Accepted

## Context
Raw image and video media blobs consume massive bandwidth and introduce copyright and privacy concerns.

## Decision
Store only identifiers, metadata counts, and 64-bit SimHash text fingerprints. Never persist raw image or video files.

## Consequences
Drastically reduces storage overhead and satisfies GDPR/CCPA data minimization principles.