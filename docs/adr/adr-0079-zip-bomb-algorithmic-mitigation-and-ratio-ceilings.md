# ADR-0079: Zip-Bomb Algorithmic Mitigation and Compression Ratio Ceilings

## Status
Accepted

## Context
Malicious archives can exhaust memory or disk space using decompression amplification (e.g. 42.zip).

## Decision
Implement strict pre-extraction inspection with a max compression ratio threshold of 100:1 and an uncompressed ceiling of 150MB total / 50MB per single file.

## Consequences
Detects and rejects zip bombs in constant time before disk decompression starts.
