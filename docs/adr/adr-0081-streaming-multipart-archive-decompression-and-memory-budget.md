# ADR-0081: Streaming Multipart Archive Decompression and Memory Budget

## Status
Accepted

## Context
Uploading multi-gigabyte or concurrent archives directly into RAM causes Out-Of-Memory (OOM) pod crashes.

## Decision
Buffer uploaded archive streams in temporary spool files (`tempfile.NamedTemporaryFile`) with chunked reads (1MB chunks) and explicit cleanup in `finally` blocks.

## Consequences
Memory consumption is bounded to O(1) buffer size regardless of uploaded archive file size.
