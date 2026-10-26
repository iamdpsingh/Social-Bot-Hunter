# Privacy and retention

## Principles

* Collect the minimum needed for the analysis, and store derived values instead of raw content where
  that is enough.
* Investigation support only. No automated enforcement, no harassment, no doxxing, no mass targeting.
* Do not bypass privacy settings, authentication or platform access controls.
* Everything stored can be traced to its source (provenance) and can be deleted.

## What is stored

| Data | Stored? | Notes |
|---|---|---|
| Platform account IDs, usernames, display names | Yes | Usernames and display names are mutable attributes, kept with observation history |
| Counts (followers, following, posts) and profile flags | Yes | `NULL` when not observed |
| Relationship edges | Yes | Directed; per scan |
| **Raw post text** | **No** | Only an exact hash, a SimHash, the text length and engagement counts |
| Account creation time | Only if the source supplied it | Never inferred |
| Raw input rows | No | Only a SHA-256 of each account row; rejected rows are kept in quarantine **with post text replaced by a length marker** |
| Credentials / tokens | Not applicable yet | No adapter exists. Production secrets belong in Secret Manager, never in the database, logs or the repository |
| Logs | Counts and scan IDs only | No usernames, no content, no tokens (tested) |

Tests assert that distinctive post text never appears anywhere in the database, in quarantine, or in
logs.

## Collection basis

Datasets are supplied by the user, with a mandatory `source_description` and `collection_method`.
The importer cannot check whether a third party's dataset was collected lawfully or within platform
terms: **that responsibility stays with whoever imports it.** Synthetic data is labelled and carries
no personal data.

## Retention and deletion (implemented)

* `python -m sbh delete-scan SCAN_ID --actor NAME` deletes everything the scan produced (edges,
  observations, content fingerprints, features, assessments, clusters, evidence, coverage, quarantine,
  checkpoints, import record) in **one transaction**, then removes any account that no remaining scan
  references. A running scan is refused.
* `python -m sbh retention-sweep --days N` deletes finished scans older than N days.
* **Audit events are kept on purpose.** They record that a deletion happened, who requested it and
  row counts, but not the deleted content.
* Model versions and the capability registry are configuration, not personal data, and are kept.
* After deletion the same input can be imported again (its hash is freed).

Not yet implemented: a configurable default retention period applied automatically, deletion of a
single account across all scans (a "right to erasure" request for one person), and deletion of
objects in Cloud Storage (none are written yet). Decide the retention period with whoever owns the
legal basis; this document should then state it.

## Access control

Not implemented yet. The CLI has no authentication and writes `actor` as a free-text label. Role-based
access control, restricted exports and per-user audit identity arrive with the API in Phase 4. Until
then, run the tool only in an environment where everyone with shell access may see all data in the
database.

## Export safety

`sbh.shared.safety.csv_safe_cell` neutralises spreadsheet formula injection (cells starting with
`= + - @`), because usernames and display names come from untrusted input. No export feature exists
yet; when it does it must use this helper. Imported values are stored verbatim.

## Incident response (for the future deployed system)

If credentials leak, a dataset was imported without the right to use it, or data is exposed: stop
the affected workers, revoke or rotate credentials, delete the affected scans with `delete-scan`
(which writes the audit event), record what happened in the audit trail and the incident log, and
notify according to the applicable law and agreements. This procedure needs an owner and a contact
list before production use.
