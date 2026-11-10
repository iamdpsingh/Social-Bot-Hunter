# RUNBOOK-0085: Debugging Twitter Archive JS Syntax Mutations

## Purpose
Troubleshoot Twitter data archive parsing failures when X changes JavaScript variable assignment prefixes.

## Steps
1. Inspect `data/tweet.js` first 200 characters.
2. Check regex matching in `TwitterArchiveParser._strip_js_prefix`.
3. Verify trailing semicolon stripping.
4. Update parser pattern if X alters assignment prefix syntax.
