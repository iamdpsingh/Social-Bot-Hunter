# Platform access matrix

This document says what Social Bot Hunter can and cannot collect, and how far each claim has been
verified. **No live platform integration exists yet.** The only working collection mode is dataset
import (CSV or JSON), which is platform-agnostic.

The table below is generated from `sbh.contracts.capabilities.default_registry()` and checked by
`python -m sbh docs`. Edit the registry in code, not this table.

## Status vocabulary

| Status | Meaning |
|---|---|
| `implemented` | Code exists and is tested, but has not been run against the real platform. |
| `verified` | Passed a real integration test in an authorised environment. The registry refuses this status without a verification date and an evidence reference. |
| `requires_approval` | The platform gates the operation behind an app review or partner programme. |
| `unsupported` | Documented as not offered. |
| `temporarily_unavailable` | Normally available, currently failing (outage, quota exhausted). |
| `not_configured` | No adapter, or no credentials. Also the state of everything not yet researched. |

`supported = unknown` means nobody has established the answer from official documentation yet.
That is deliberately different from `no`.

<!-- BEGIN GENERATED:capabilities -->
| Platform | Operation | Mode | Status | Supported | Endpoint / version | Verified |
|---|---|---|---|---|---|---|
| instagram | dataset_import | dataset_import | implemented | yes | - | never |
| instagram | list_content | official_api | not_configured | unknown | - | never |
| instagram | list_followers | official_api | not_configured | unknown | - | never |
| instagram | list_following | official_api | not_configured | unknown | - | never |
| instagram | lookup_account | official_api | not_configured | unknown | - | never |
| linkedin | dataset_import | dataset_import | implemented | yes | - | never |
| linkedin | list_content | official_api | not_configured | unknown | - | never |
| linkedin | list_followers | official_api | not_configured | unknown | - | never |
| linkedin | list_following | official_api | not_configured | unknown | - | never |
| linkedin | lookup_account | official_api | not_configured | unknown | - | never |
| tiktok | dataset_import | dataset_import | implemented | yes | - | never |
| tiktok | list_content | official_api | not_configured | unknown | - | never |
| tiktok | list_followers | official_api | not_configured | unknown | - | never |
| tiktok | list_following | official_api | not_configured | unknown | - | never |
| tiktok | lookup_account | official_api | not_configured | unknown | - | never |
| x | dataset_import | dataset_import | implemented | yes | - | never |
| x | list_content | official_api | not_configured | unknown | - | never |
| x | list_followers | official_api | not_configured | unknown | - | never |
| x | list_following | official_api | not_configured | unknown | - | never |
| x | lookup_account | official_api | not_configured | unknown | - | never |
| youtube | dataset_import | dataset_import | implemented | yes | - | never |
| youtube | list_content | official_api | not_configured | unknown | - | never |
| youtube | list_followers | official_api | not_configured | unknown | - | never |
| youtube | list_following | official_api | not_configured | unknown | - | never |
| youtube | lookup_account | official_api | not_configured | unknown | - | never |
<!-- END GENERATED:capabilities -->

## Why every live operation is `not_configured`

Endpoints, OAuth scopes, API versions and approval requirements change often and differ a lot
between platforms. The registry therefore holds **no endpoint, scope or version** for any live
operation, because none has been checked against current official documentation. Writing them from
memory would produce a table that looks authoritative and may be wrong.

No architecture can guarantee complete follower/following access on every network. Expect that
several of these operations will turn out to be unavailable, restricted to the authenticated
account's own data, or gated behind paid tiers or approval. When that is confirmed the registry
should say `unsupported` or `requires_approval`, and the product continues to work through dataset
import for those platforms.

## Research checklist before implementing an adapter (Phase 5/6)

For each platform and each operation (`lookup_account`, `list_followers`, `list_following`,
`list_content`), answer from the platform's current official developer documentation and record the
source and date:

1. Does an official endpoint exist for this operation on **third-party** accounts, or only for the
   authenticated user's own account?
2. Endpoint path and API version.
3. Required OAuth scopes, and whether an app review or partner approval is needed.
4. Pagination style, page size, and whether the list can be enumerated completely.
5. Rate limits and quotas, and what the platform says to do on a 429.
6. Terms-of-service and data-retention conditions on stored data.
7. Cost tier required, if any.

Then implement the adapter against `sbh.contracts.adapter.PlatformAdapter`, write an integration test
that runs against an authorised environment, and only then set `status=verified` with the
verification date and a reference to that test run.

## Collection modes

| Mode | Status |
|---|---|
| Official API integration | Contract defined (`PlatformAdapter`, `AccessOutcome`); no adapter implemented. |
| Dataset import | Implemented and tested. See `data-dictionary.md` for the import format. |
| Permitted public-data collection | Not implemented. Would be added only for sources and methods that the platform terms and applicable law allow. |

The system never bypasses private-account restrictions, authentication, rate limits or anti-bot
controls, never uses session cookies or stolen credentials, and never fabricates missing follower
lists. Unavailable data is reported as unavailable.
