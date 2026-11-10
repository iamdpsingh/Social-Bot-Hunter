# ADR-0080: Hardened Archive Path Traversal and Symlink Denial

## Status
Accepted

## Context
Archives containing `../`, leading slashes, drive letters, or symlinks can overwrite system files or read sensitive host secrets.

## Decision
Reject any archive containing relative directory escapes (`..`), absolute paths, null bytes (`\x00`), or symbolic links (`SYMTYPE`).

## Consequences
All extracted entries are verified to be strictly sub-paths of the allocated quarantine target directory.
