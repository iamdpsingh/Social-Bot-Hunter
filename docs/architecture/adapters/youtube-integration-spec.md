# Social Bot Hunter - YouTube Data API v3 Integration Specification

## 1. Overview
The YouTube adapter interfaces with Google's YouTube Data API v3 to ingest channel metadata,
recent uploaded videos, and subscription relationships.

## 2. Quota Management
- **Daily Budget**: 10,000 units default per GCP project.
- **Cost Allocation**:
  - `channels.list`: 1 unit
  - `playlistItems.list`: 1 unit
  - `subscriptions.list`: 1 unit
  - `search.list`: 100 units (prohibited during routine scans; upload playlist derivation is used instead).
- **Upload Playlist Optimization**: Rather than querying `search.list` for 100 units, the adapter converts the channel's canonical ID `UC[22]` to its upload playlist `UU[22]`, querying `playlistItems.list` for 1 unit—a 99% quota saving.

## 3. Permission Boundaries
- **Public Data**: Channel name, bio, subscriber count, avatar, video count, view count.
- **Restricted Data**: Channel subscriber lists cannot be enumerated publicly. Attempting to list followers yields `AccessOutcome.REQUIRES_APPROVAL` with clear OAuth 2.0 instructions.
