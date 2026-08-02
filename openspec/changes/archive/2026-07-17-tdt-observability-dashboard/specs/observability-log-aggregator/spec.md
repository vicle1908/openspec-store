# observability-log-aggregator

## ADDED Requirements

### Requirement: Log Sources Discovered from Config or Defaults
The log aggregator SHALL discover log file sources from `~/.tdt/observability/log-sources.yaml`. When that file is absent, it SHALL use these default patterns covering all TDT log producers:

- `~/.tdt/logs/*.log` — all service logs (excluding rotated backups `*.1.log`, `*.2.log`, etc.)
- `~/.tdt/logs/jira-daily-reports/**/*.log` — Jira report scheduler logs
- `~/.tdt/deployments/*/logs/*.log` — deployment-specific logs

#### Scenario: Uses default patterns when config absent
- **WHEN** `~/.tdt/observability/log-sources.yaml` does not exist
- **THEN** the aggregator SHALL watch the three default pattern groups above

#### Scenario: Loads custom sources from config
- **WHEN** `~/.tdt/observability/log-sources.yaml` exists with a `sources` list
- **THEN** the aggregator SHALL watch each path and SHALL NOT fall back to defaults

### Requirement: Parses Two Distinct Log Formats from the TDT Ecosystem
The log aggregator SHALL handle two log formats used across TDT services:

**Format A — structlog JSON** (webhook-receiver, agent-core, ai-review):

```json
{"event": "handoff_scheduled", "level": "info", "logger": "webhook_receiver.api.app", "timestamp": "2026-07-03T07:01:07.123456+07:00", "handoff_id": "h-xxx", "service": "webhook-receiver"}
```

Fields: `timestamp` (ISO 8601), `level` (debug/info/warning/error), `logger` (module path), `event` (string), plus any `event_kwargs` as additional keys.

**Format B — Plain text** (jira-daily-reports, jira-reminders):

```
2026-07-03T07:01:07+0700 INFO jira_daily_reports.reports.sprint_report_sheet sprint_sheet_run_done total=39 met=6 behind=32
```

Pattern: `<ISO-timestamp> <LEVEL> <logger.module> <message>`. The first word of `<message>` is the `event_type`.

#### Scenario: Parses valid structlog JSON line
- **WHEN** a line is valid JSON with `timestamp`, `level`, `logger`, and `event` keys
- **THEN** the aggregator SHALL parse it, set `event_type = event`, `message = event`, and store additional keys in `extra`

#### Scenario: Parses plain text jira-daily-reports line
- **WHEN** a line matches the plain-text pattern with ISO timestamp and LEVEL
- **THEN** the aggregator SHALL parse timestamp, level, logger, and message, and set `event_type` to the first whitespace-delimited word of the message

#### Scenario: Skips unparseable lines without crashing
- **WHEN** a line cannot be parsed as JSON or matched to the text pattern (e.g., multi-line traceback, binary data)
- **THEN** the aggregator SHALL log a debug message and skip the line

### Requirement: Events Enriched with Ingest Metadata and Derived Fields
Each parsed event SHALL be enriched with:

- `ingest_timestamp` — local timestamp when the event was ingested
- `source_file` — absolute path of the log file
- `service` (column) populated from a `service_name` (Python field) derived from the `logger` field's first dot-separated segment, with underscores replaced by hyphens (e.g., `jira_daily_reports.reports.sprint_report_sheet` → `jira-daily-reports`)
- `event_type` — the `event` field for structlog JSON, or the first word of the message for plain text

#### Scenario: Derives service_name from jira-daily-reports logger path
- **WHEN** the parsed logger is `jira_daily_reports.reports.sprint_report_sheet`
- **THEN** the enriched event SHALL have `service_name="jira-daily-reports"`

### Requirement: Batch Insert to DuckDB with Flush Policy
The log aggregator SHALL batch events and insert them into DuckDB at `~/.tdt/observability/events.duckdb` in the `events` table. The batch SHALL be flushed when EITHER of these conditions is met:

- 5 seconds have elapsed since the last flush (time-based)
- The batch contains 500 or more events (size-based)

A flush SHALL wrap all rows in a single explicit transaction (`BEGIN` / `COMMIT` / `ROLLBACK`). This was adopted after observing (2026-07-04) that per-row auto-commit on macOS can take minutes for the `MetaTransaction::Commit` call to complete on a 100K-event backlog flush, holding the DuckDB writer lock for so long that downstream processes (dashboard readers, retention workflow) starve. With an explicit transaction, the WAL is flushed once at `COMMIT` instead of once per row.

If any row insert raises, the entire batch SHALL be rolled back (defensively via `contextlib.suppress` because the connection may already be in a broken state), the connection SHALL be closed, and the next flush SHALL retry the full batch from a fresh connection.

#### Scenario: Flushes on size threshold
- **WHEN** the batch buffer reaches 500 events before the 5-second timer
- **THEN** the aggregator SHALL wrap all 500 rows in a single transaction and commit atomically, then reset the buffer

#### Scenario: Flush rollback on per-row failure
- **WHEN** any row insert raises an exception (e.g. constraint violation, malformed JSON in `extra`)
- **THEN** the aggregator SHALL roll back the transaction, close the connection, and retain the batch for the next flush attempt — never dropping events silently

#### Scenario: Single transaction commits on success
- **WHEN** all 500 rows insert cleanly within one transaction
- **THEN** exactly one `COMMIT` is issued, the WAL is fsynced once, and the connection is closed so the lock is released

### Requirement: DuckDB Events Table Created with Proper Schema
The store SHALL create the `events` table on first run using `IF NOT EXISTS`:

```sql
CREATE TABLE events (
  timestamp TIMESTAMP,
  service VARCHAR,
  level VARCHAR,
  event_type VARCHAR,
  trace_id VARCHAR,
  message TEXT,
  extra JSON,
  ingest_timestamp TIMESTAMP,
  source_file VARCHAR
);

CREATE INDEX idx_events_time_service_level ON events(timestamp, service, level);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_trace_id ON events(trace_id);
```

#### Scenario: Events table created idempotently on first run
- **WHEN** `DuckDBStore.init_db()` is called for the first time on a new database file
- **THEN** it SHALL create the `events` table and its three indexes
- **AND** subsequent calls SHALL succeed without error

### Requirement: File Offset Tracking and Log Rotation Detection
The log aggregator SHALL track the byte offset of the last-read position for each watched file. When a file is rotated, the aggregator SHALL detect this via inode comparison and reopen from the beginning.

Offset and inode state SHALL be persisted to `~/.tdt/observability/log-aggregator-state.json` after every successful flush, using atomic tmp-file-then-rename semantics. On startup the aggregator SHALL load this file and resume from the persisted offset for any file whose persisted inode still matches the current inode. This avoids re-ingesting the entire history of every watched file on each launchd restart (which on macOS would duplicate ~109 K events from a single 26 MB log per restart).

On startup the aggregator SHALL perform an initial backfill (offset 0 → EOF) for any watched file that has NO persisted offset record, OR whose persisted inode no longer matches the current inode (file was rotated/replaced). Files with a matching persisted inode are resumed from their persisted offset — the backfill phase becomes a no-op for them.

Watched paths SHALL be normalized with `os.path.realpath` before being recorded in the offset/inode maps and before being used as lookup keys in the watch loop. On macOS, `/var/folders` is a symlink to `/private/var/folders`; some APIs (e.g., `tempfile.TemporaryDirectory`, the source path passed to `watchfiles.awatch`) return one form while the change events emit the other. Without normalization, the watch loop would look up an offset key that does not exist and re-read from offset 0, silently duplicating every event.

#### Scenario: Tracks position across reads
- **WHEN** the aggregator reads from a log file and reaches EOF
- **THEN** it SHALL record the final byte offset and resume from that position on the next read

#### Scenario: Detects log rotation via inode change
- **WHEN** the aggregator calls `os.stat(path).st_ino` and the result differs from the stored inode
- **THEN** it SHALL close the old file handle, reset the offset to 0, and read from the beginning of the new file

#### Scenario: Backfills on first start or after rotation
- **WHEN** the aggregator starts and a watched file has no persisted offset record OR its inode has changed since the last persist
- **THEN** it SHALL read all existing lines from offset 0, parse them, and ingest them on the first flush after startup

#### Scenario: Resumes from persisted offset on subsequent starts
- **WHEN** the aggregator starts and a watched file has a persisted offset whose inode still matches the current inode
- **THEN** it SHALL resume reading from the persisted offset and SHALL NOT re-ingest content already in DuckDB

#### Scenario: Normalizes symlinked paths to prevent silent re-ingestion
- **WHEN** a watched file path resolves through a symlink (e.g., `/var/folders/...` → `/private/var/folders/...`)
- **THEN** both the discovery step and the change-event dispatch step SHALL canonicalize via `os.path.realpath` so the offset/inode lookup hits the same key

### Requirement: Data Retention Policy
Log events SHALL be retained in DuckDB for 30 days. The log aggregator or a separate cleanup job SHALL run a daily DELETE statement removing events older than 30 days. Health snapshots SHALL be retained for 90 days.

The log aggregator SHALL release the DuckDB writer lock between flushes so the cleanup job (which may run from a different process via the scheduler service) can acquire it. The connection is opened on each `_flush_batch()` call and closed in the `finally` block — the aggregator never holds the events DuckDB connection across flushes.

The cleanup job SHALL use exponential-backoff retry with a 180-second total budget to acquire the lock across the 5-second log-collector flush cycle and the 30-second health-poller cycle.

#### Scenario: Cleanup removes events older than 30 days
- **WHEN** the cleanup job runs (daily at 02:00 UTC)
- **THEN** it SHALL execute `DELETE FROM events WHERE timestamp < NOW() - INTERVAL '30 days'`

#### Scenario: Cleanup removes health snapshots older than 90 days
- **WHEN** the cleanup job runs
- **THEN** it SHALL execute `DELETE FROM health_snapshots WHERE timestamp < NOW() - INTERVAL '90 days'`

#### Scenario: Cleanup acquires lock during contention
- **WHEN** the log-aggregator or health-poller holds the events DuckDB lock
- **THEN** the cleanup job SHALL retry with exponential backoff (2s → 4s → 8s → …, capped at 30s per sleep, 180s total budget) until the lock is released
- **AND** if the budget is exhausted, log `retention_lock_budget_exhausted` with attempts and budget_seconds, and return a `-1` marker instead of raising

### Requirement: Background Process with Lifecycle Management
The log aggregator SHALL run as a background daemon with graceful shutdown on SIGTERM and SIGINT. Pending events SHALL be flushed to DuckDB before exit. A PID file SHALL be written to `~/.tdt/observability/log-aggregator.pid`.

#### Scenario: Graceful shutdown flushes pending events
- **WHEN** the aggregator receives SIGTERM
- **THEN** it SHALL flush the remaining batch, close all file handles, remove the PID file, and exit with code 0

### Requirement: Singleton via PID-File with Stale-PID Detection
On startup the aggregator SHALL refuse to start if the PID file points at a live process. If the recorded PID is dead (e.g. after a crash), the PID file SHALL be overwritten and startup SHALL proceed. This guards against the duplicate-process class of bug observed on 2026-07-05 where two `log_collector` processes ran concurrently because launchd's `KeepAlive=true` auto-restarted the daemon while the original instance was still alive but its PID file had been overwritten.

#### Scenario: Second instance refuses to start
- **WHEN** a second `log_collector` is launched while the recorded PID is alive
- **THEN** it SHALL print `ERROR: another log collector is already running (PID <pid>)` to stderr and exit with code 1

#### Scenario: Stale PID is overwritten on restart
- **WHEN** a `log_collector` starts and the recorded PID is no longer alive (kernel returns `ESRCH` for `kill -0`)
- **THEN** the PID file SHALL be overwritten with the new PID and startup SHALL proceed

#### Scenario: Detecting an orphan instance
- **WHEN** an operator suspects duplicate instances (e.g. events stall despite the daemon appearing alive)
- **THEN** the runbook SHALL provide a one-liner that lists all `tdt_observability.log_collector` PIDs and the `log-aggregator.pid` content so they can be reconciled

### Requirement: Flush Errors Are Observable
A failed batch flush SHALL NOT be silent. The aggregator SHALL log the error to stderr (where launchd captures it) and SHALL keep the in-memory batch intact for the next flush attempt. A periodic heartbeat line SHALL be emitted to stderr at least every 60 seconds when the collector is alive and idle, so operators can distinguish "process is running" from "process is silently stalled".

#### Scenario: Flush failure surfaces in stderr
- **WHEN** `insert_events_batch` raises (lock held, malformed row, etc.)
- **THEN** the aggregator SHALL print the exception class and message to stderr with the batch size, retain the batch for retry, and continue to the next watch tick

#### Scenario: Heartbeat when no source file is changing
- **WHEN** 60 seconds elapse without any successful flush (no events arriving or no source-file changes)
- **THEN** the aggregator SHALL emit a `[heartbeat]` line to stderr including the file count so operators can confirm the process is alive
