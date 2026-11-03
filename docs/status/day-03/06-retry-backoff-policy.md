# Day 3: Retry & Backoff Policy Status

Worker task failures trigger exponential backoff:
- Base delay: 100ms
- Exponential factor: 2x per attempt
- Max retries: 3 attempts before permanent transition to `failed`.
