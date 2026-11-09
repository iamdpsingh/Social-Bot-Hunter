# ADR-0074: Unified Profile URL Parsing with Automated Platform Detection

## Status
Accepted

## Context
Users input raw links from various platforms and devices (desktop, mobile, apps).

## Decision
Autodetect platform from host (youtube, twitter, x, instagram, tiktok), strip tracking query parameters, and normalize to canonical profile URLs.

## Consequences
Provides seamless user experience and SSRF security.