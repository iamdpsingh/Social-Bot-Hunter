# ADR-0083: Official Twitter Archive JavaScript Manifest Parsing

## Status
Accepted

## Context
Twitter/X GDPR data download archives wrap raw JSON inside JavaScript window assignment statements (`window.YTD.tweet.part0 = [...];`).

## Decision
Implement `TwitterArchiveParser` with regex-based JS variable assignment stripping and trailing semicolon sanitation before JSON deserialization.

## Consequences
Seamless ingestion of standard Twitter archive downloads into `ContentRecord` domain entities with SimHash fingerprints.
