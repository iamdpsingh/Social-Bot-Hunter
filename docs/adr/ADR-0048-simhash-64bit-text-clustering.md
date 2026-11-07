# ADR-0048: 64-Bit SimHash Text Fingerprinting for Near-Duplicate Bot Message Clustering

## Context
Coordinated botnets frequently blast slightly modified messages (inserting random tokens, varying punctuation, or replacing synonyms) to circumvent naive string equality checks.

## Decision
We implement a 64-bit SimHash algorithm using word unigram hashing and vector sign summation. Messages with a Hamming distance <= 12 bits are grouped into near-duplicate campaign clusters.

## Consequences
- Fast O(N) fingerprint generation with minimal CPU overhead.
- Near-duplicate clustering accurately captures templated propaganda and spam campaigns.
