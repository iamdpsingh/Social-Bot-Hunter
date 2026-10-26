# Security & Privacy Rules

These rules enforce credential protection, data minimisation, and privacy compliance.

## Principles

1. **Zero Credential Commits**: Never commit API keys, tokens, client secrets, passwords, or private keys to the git repository. Enforce automated secret scanning in pre-commit and CI.
2. **No Token or PII Logging**: Never log OAuth access tokens, session cookies, raw post contents, or personal email addresses. Sanitize all logging context.
3. **Least Privilege**: Grant only the minimal OAuth scopes, database privileges, and GCP IAM permissions necessary to perform the requested operation.
4. **Input & Upload Sanitization**: Validate and sanitize all dataset imports and file uploads to prevent path traversal, SQL injection, and malicious payloads.
5. **No Harassment or Doxxing**: The platform is an investigation and analytical tool for inauthentic coordination. It must never be used for harassment, doxxing, mass spamming, or automated unauthorized enforcement.
6. **Retention & Deletion**: Implement verifiable retention policies and hard-deletion routines for raw data, ensuring compliance with privacy regulations (GDPR/CCPA/platform policies).
