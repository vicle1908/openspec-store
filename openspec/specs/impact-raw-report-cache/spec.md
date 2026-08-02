# impact-raw-report-cache Specification

## Purpose
TBD - created by archiving change impact-sheet-integration. Update Purpose after archive.
## Requirements
### Requirement: RawReportCache class
The system SHALL expose a `RawReportCache` class in `jira_skill.impact.impact_report` that owns the on-disk JSON cache lifecycle. The class MUST expose `get()`, `put()`, and `invalidate()` methods, all keyed on the tuple `(project_path, mr_iid, commit_sha)`. The default cache directory SHALL be `$TDT_HOME/state/webhook-receiver/webhook-impacts/`, and the default TTL SHALL be 24 hours.

#### Scenario: get returns fresh cache
- **WHEN** a report file exists at `<state_dir>/webhook-impacts/<mr_iid>-<sha12>.json`
- **AND** the file's mtime is within `ttl_hours` of now
- **THEN** `cache.get()` MUST return a `CachedImpactReport` with `is_fresh() == True`

#### Scenario: get returns None when stale
- **WHEN** a report file exists but its mtime is older than `ttl_hours`
- **THEN** `cache.get()` MUST return `None`
- **AND** the caller MUST be free to re-run the pipeline and overwrite the file

#### Scenario: get returns None when missing
- **WHEN** no file exists at the expected path
- **THEN** `cache.get()` MUST return `None`
- **AND** MUST NOT raise

#### Scenario: get deletes corrupt file
- **WHEN** the file exists but its JSON is invalid or fails `ImpactReport.model_validate()`
- **THEN** `cache.get()` MUST delete the file
- **AND** MUST return `None`
- **AND** MUST log a warning

#### Scenario: put persists a report
- **WHEN** `cache.put(report)` is called with a valid `ImpactReport`
- **THEN** the file MUST be written to `<state_dir>/webhook-impacts/<mr_iid>-<sha12>.json`
- **AND** MUST return a `CachedImpactReport` wrapper

### Requirement: read_raw_report standalone function
The system SHALL expose a standalone `read_raw_report(project_path, mr_iid, commit_sha, state_dir=None) -> CachedImpactReport | None` function that does NOT apply a TTL check (it returns the raw file regardless of age). It MUST be the inverse of `write_raw_report`. Used by tests and by `RawReportCache.put()` to read back what it just wrote.

#### Scenario: read_raw_report mirrors write_raw_report
- **WHEN** a report is written via `write_raw_report(report, state_dir=dir)`
- **THEN** `read_raw_report(report.project_path, report.mr_iid, report.commit_sha, state_dir=dir)` MUST return a `CachedImpactReport` wrapping the same `ImpactReport`
- **AND** MUST round-trip all fields without data loss

### Requirement: Cache naming convention
The cache filename MUST follow `<mr_iid>-<sha12>.json` where `<sha12>` is the first 12 characters of the commit SHA. When the SHA is empty, the suffix MUST be `unknown`. This naming is shared with the existing `write_raw_report` and MUST NOT be changed.

#### Scenario: SHA-stamped filename
- **WHEN** `commit_sha = "abc123def4567890"`
- **THEN** the cache filename MUST be `<mr_iid>-abc123def456.json`

#### Scenario: Unknown SHA filename
- **WHEN** `commit_sha = ""` or `None`
- **THEN** the cache filename MUST be `<mr_iid>-unknown.json`

### Requirement: Concurrent cache access safety
The `RawReportCache` SHALL assume single-process use. Concurrent reads from multiple threads within the same process MUST be safe (read-only). Concurrent writes MUST be the responsibility of the caller (the `concurrency` semaphore in `ImpactEnricher` bounds parallelism to a default of 8).

#### Scenario: Reads do not corrupt under concurrency
- **WHEN** multiple asyncio coroutines call `cache.get()` for the same key concurrently
- **THEN** each MUST receive a valid `CachedImpactReport` (or `None`) without raising
- **AND** the file content MUST NOT be partially read

