# Social Bot Hunter - Profile URL Normalization Specification

## Overview
Social Bot Hunter ingests target account identifiers from user input, webhooks, and scan jobs.
To prevent Server-Side Request Forgery (SSRF), internal port scanning, and profile ambiguity, all URLs must pass through the `validate_profile_url` pipeline.

## Supported Platform Syntaxes

### 1. YouTube
- **Handles**: `https://www.youtube.com/@handle` or bare `@handle`
  - Canonical format: `https://www.youtube.com/@handle`
  - Constraint: 3 to 30 alphanumeric, underscore, dot, or hyphen characters.
- **Canonical Channel IDs**: `https://www.youtube.com/channel/UC...` or bare `UC...`
  - Canonical format: `https://www.youtube.com/channel/UC[22-chars]`
  - Constraint: Exactly 24 characters beginning with `UC`.
- **Legacy & Custom URLs**: `/c/CustomName` or `/user/LegacyName`
  - Flags `is_canonical=False` to trigger resolution to canonical channel ID during preflight probe.
- **Video URLs**: `/watch?v=...`, `youtu.be/...`, and `/shorts/...` are rejected immediately.

### 2. X (Twitter)
- **Usernames**: `https://x.com/username`, `https://twitter.com/username`, or bare `@username`
  - Domain `twitter.com` is automatically rewritten to `x.com`.
  - Constraint: 1 to 15 alphanumeric or underscore characters.
  - Reserved routes (`explore`, `home`, `messages`, `settings`, `about`, etc.) are rejected with HTTP 400.
  - Query parameters and tracking fragments (`?s=20`, `?ref_src=...`) are stripped.

### 3. Bluesky
- **Handles**: `https://bsky.app/profile/alice.bsky.social` or bare `alice.bsky.social`
- **DIDs**: `did:plc:z72i7hdynmk6r22z27h6tvur`

## Security Guardrails
- **Scheme Whitelist**: Only `http` and `https` permitted. All pseudo-schemes (`javascript:`, `file:`, `data:`, `gopher:`) raise `InvalidUrlError`.
- **SSRF Defense**: Reject hostnames resolving to RFC1918 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.1`, `localhost`), and cloud metadata (`169.254.169.254`).
- **Maximum Length**: URLs exceeding 2048 characters are rejected.
