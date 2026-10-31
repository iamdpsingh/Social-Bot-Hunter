# Monitoring runbook

Scope today: the CLI/library pipeline. There is no deployed service, no Cloud Monitoring and no
alerting yet; the alert definitions at the end are the plan. The diagnostic SQL below was run against a
real scan database and executes as written (SQLite syntax; it is also valid PostgreSQL). Replace `:s`
with the scan ID.

**Principle:** a pipeline failure is an operational event about a scan. It is never evidence about an
account. A failed or partial scan produces no findings from the missing data, and the dashboard must
show it as incomplete rather than as "no suspicious accounts".

Logs are JSON on stderr (`python -m sbh -v ...`) with a `scan_id` on every line. They contain counts and
IDs only.

## First look

```sql
-- recent problems
SELECT id, platform, status, failure_reason, finished_at FROM scan_jobs
 WHERE status = 'failed' ORDER BY finished_at DESC;
-- scans that may be stuck
SELECT id, started_at FROM scan_jobs WHERE status = 'running' ORDER BY started_at;
-- what happened to one scan
SELECT occurred_at, action, details FROM audit_events WHERE subject_id = :s ORDER BY occurred_at;
SELECT stage, cursor_pos, status, updated_at FROM scan_checkpoints WHERE scan_id = :s ORDER BY updated_at;
```

## Failure categories

### 1. Import rejected before a scan exists

*Symptom:* CLI prints `error: ...`; no new row in `scan_jobs`.
*Cause:* unreadable input: bad manifest, unsupported `schema_version`, missing required CSV column,
file over the size or row limit, NUL bytes, invalid JSON.

```sql
SELECT occurred_at, actor, details FROM audit_events WHERE action = 'import_rejected' ORDER BY occurred_at DESC;
```
*Recover:* fix the input and import again. Nothing was written.

### 2. Scan `failed`: too many invalid records

*Symptom:* `failure_reason` starts `too_many_invalid_records`.
*Cause:* more than `imports.max_invalid_fraction` (default 20%) of rows were rejected, which usually
means a wrong column mapping, wrong platform, or wrong timestamp format.

```sql
SELECT entity, kind, reasons, COUNT(*) AS n FROM quarantined_records WHERE scan_id = :s
 GROUP BY entity, kind, reasons ORDER BY n DESC;
```
*Recover:* the dominant `reasons` value names the problem. Fix the source and import again (a changed
file has a new hash, so it is a new scan). Nothing from the failed scan was imported. Delete the failed
scan with `python -m sbh delete-scan ID` if you do not want to keep its quarantine rows.

### 3. Scan `failed`: exception during a stage

*Symptom:* `failure_reason` is `ExceptionType: message`; checkpoints show how far it got.
*Cause:* database error, disk full, a bug, or a configuration conflict (see 8).
*Recover:* fix the cause, then **run the same import again**. The scan resumes from its last committed
checkpoint (tested to give the same result as an uninterrupted run). The earlier reason is kept in
`status_detail.failure_history`.

### 4. Scan stuck `running`

*Symptom:* status `running` for far longer than a normal run; re-import raises `ScanInProgressError`.
*Cause:* the process was killed (`kill -9`, OOM, host restart) so it could not mark the scan failed.
*Check first* that no worker is alive for this scan. Two workers on one scan is the one thing that must
not happen.
*Recover:* `python -m sbh import SOURCE --allow-resume-running`. This resumes from checkpoints and
writes a `scan_resumed` audit event.

### 5. Scan `partial`

*Symptom:* scan finished with status `partial`. This is a valid outcome, not an error.
*Cause:* see the reasons the scan stored:

```sql
SELECT status_detail FROM scan_jobs WHERE id = :s;   -- partial_reasons, data_quality_warnings, graph_error
SELECT list_kind, completeness, COUNT(*) AS n FROM relationship_list_coverage WHERE scan_id = :s
 GROUP BY list_kind, completeness;
```
Typical reasons: relationship lists declared `partial` or `unknown`; rejected rows; graph analysis skipped.
*Action:* nothing is broken. Read the limitations before drawing conclusions; scores and clusters
apply only to what was observed.

### 6. Graph analysis skipped

*Symptom:* partial reason `graph analysis skipped: more than N edges` (or nodes, candidate pairs, or
`runtime limit`); no clusters; network features unavailable (`max_following_jaccard`,
`reciprocity_ratio`).
*Cause:* the input exceeded `graph.limits` in the configuration.
*Recover:* only if the limit is genuinely too low for a legitimate workload: raise it in a new config
version, watching memory (reference: about +65 MB for 60k edges). Otherwise analyse a narrower scope.
Do not raise limits to make an alert go away. Check also the `similarity.skipped_hub_targets` count in
`status_detail` if results look thin.

### 7. Unusually many accounts with `insufficient_evidence`

```sql
SELECT status, COUNT(*) AS n FROM risk_assessments WHERE scan_id = :s GROUP BY status;
```
This is normal for accounts that appear only as follow targets (stubs). It is a data problem when
accounts that *should* have profile data are affected: check `data_quality_warnings` for high
missingness and the `limitations` of a sample assessment for the exact missing features.

### 8. Configuration conflict or migration problem

* `ConfigError: ... already registered with different configuration` means the detection config
  changed without a new `version`. Bump `version` in the YAML. Never delete the `model_versions` row
  to get past it: stored scores depend on it.
* `migration NNNN was modified after being applied` means someone edited an applied migration. Restore
  the file from version control and add a new migration instead.
* `SELECT version, applied_at FROM schema_migrations ORDER BY version;` shows what is applied.

### 9. Suspected bad data after the fact

Delete the scan (`python -m sbh delete-scan ID --actor you`). That removes everything it produced and
writes an audit event without the content.

## Metrics to watch (planned, not implemented)

When there is a deployed service, emit these from the scan records and logs:

| Signal | Source | Suggested alert |
|---|---|---|
| Scans `failed` | `scan_jobs.status` | any in the last hour |
| Scan `running` longer than N minutes | `started_at` | N = 3x the p95 run time |
| Rejected share of rows | `quarantined_records` / input rows | above half of `max_invalid_fraction` |
| Graph limit hits | `status_detail.graph_error` | any |
| Rate-limit and 5xx responses from platforms | adapter logs | sustained, once adapters exist |
| Queue depth and oldest task age | Local worker queue | once multi-process workers exist |
| Database latency, connections, storage | SQLite / Local PostgreSQL | standard thresholds |

Keep operational alerts separate from analytical findings, and route them to different places.
