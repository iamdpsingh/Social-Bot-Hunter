# Platform Integration Rules

These rules govern how Social Bot Hunter interacts with external social platforms (X, Instagram, TikTok, YouTube, LinkedIn).

## Principles

1. **Authorised Access Only**: Use only official, documented platform APIs, approved datasets, or permitted public data collection adhering strictly to platform terms and applicable laws.
2. **Pre-Implementation Verification**: Check documented endpoint capabilities, quota restrictions, required OAuth scopes, and approval requirements before writing adapter code.
3. **No Fabricated Endpoints**: Never invent endpoints, response fields, or mock permissions that do not exist in official platform developer documentation.
4. **Adapter Isolation**: All platform-specific request shaping, error translation, pagination, and response parsing must be isolated inside `sbh.contracts` or dedicated adapter modules.
5. **Honest Capability States**: Distinguish explicit integration states:
   - `not_configured`
   - `requires_approval`
   - `implemented`
   - `verified` (only after passing a real integration test against an authorised environment)
   - `unsupported`
   - `temporarily_unavailable`
6. **Graceful Degradation**: When endpoints are restricted or permissions are denied, return `AccessOutcome` with explicit reasons and lower evidence coverage rather than failing the scan or returning fabricated data.
7. **Fixtures Labelled**: Use test fixtures strictly in tests and labelled demonstrations; never substitute fixtures into live production scans.
