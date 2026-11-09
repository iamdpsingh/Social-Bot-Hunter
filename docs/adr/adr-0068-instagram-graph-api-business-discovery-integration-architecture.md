# ADR-0068: Instagram Graph API Business Discovery Integration Architecture

## Status
Accepted

## Context
Social Bot Hunter requires live inspection of Instagram accounts. Official Meta Graph API v21.0 offers Business Discovery on Connected Business/Creator accounts.

## Decision
Use Business Discovery nested queries to collect public profile fields and media while enforcing strict boundary checks when personal accounts are targeted.

## Consequences
Ensures compliant collection without unauthorized scraping.