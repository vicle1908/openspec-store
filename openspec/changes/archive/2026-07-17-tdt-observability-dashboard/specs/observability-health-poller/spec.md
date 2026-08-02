# observability-health-poller

## ADDED Requirements

### Requirement: Health Poller Discovers Services from Config or Defaults

The health poller SHALL poll health endpoints from all configured TDT ecosystem services. Service configurations SHALL be loaded from `~/.tdt/observability/config.yaml`. When that file is absent, the poller SHALL use a hardcoded default list of the three primary TDT services.

#### Scenario: Default service list when config absent

- **WHEN** `~/.tdt/observability/config.yaml` does not exist
- **THEN** the poller SHALL poll these three defaults:
  - `webhook-receiver` → `http://localhost:8080/health`
  - `ai-review` → `http://localhost:8090/health/full`
  - `tdt-scheduler` → `http://localhost:9100/scheduler/health`

#### Scenario: Custom services loaded from config file

- **WHEN** `~/.tdt/observability/config.yaml` exists with a `services` list
- **THEN** the poller SHALL load each service entry (name, url, timeout_seconds) and poll accordingly

#### Scenario: Gracefully handles unreachable services

- **WHEN** a service health endpoint is unreachable, returns non-2xx, or times out
- **THEN** the poller SHALL record the failure with `status="unreachable"` and SHALL NOT crash

### Requirement: Health Snapshots Stored in DuckDB with TDT Field Extraction

The health poller SHALL record each health check result as a snapshot in DuckDB at `~/.tdt/observability/health.duckdb`. Each snapshot SHALL contain: `timestamp`, `service_name`, `status`, `response_time_ms`, and the full `payload` JSON column. The poller SHALL also extract TDT-specific fields into dedicated columns.

The `status` field SHALL be derived from the HTTP response as follows:

- `healthy` — HTTP 200 AND no sub-check returns `warning`, `degraded`, or `error`; OR a non-200 response whose JSON body has `status` in `{"healthy", "ready"}` (rare fallback)
- `degraded` — HTTP 200 AND any sub-check returns `warning` or `degraded`, OR top-level `status` is `"degraded"`; OR a non-200 response whose JSON body has `status` in `{"degraded", "unhealthy"}` (the service is responding but reports itself as not fully healthy)
- `unreachable` — request exception (timeout, connection refused, DNS failure), HTTP non-2xx without a parseable `status` field in the body, or an HTTP 4xx response (the service is not responding correctly)

#### Scenario: HTTP 503 with degraded body classifies as degraded

- **WHEN** a TDT service returns HTTP 503 with body `{"status": "degraded", "checks": {...}}` (the standard self-report when an internal check fails)
- **THEN** the poller SHALL insert a row with `status="degraded"` and SHALL record `error_kind="http_error"`, `body_status="degraded"`, and `detail="HTTP 503"` in the payload
- **AND** it SHALL NOT alert as unreachable — the service is responding, just not fully healthy

#### Scenario: HTTP 503 with non-JSON body classifies as unreachable

- **WHEN** an upstream proxy or load balancer returns HTTP 503 with an HTML error page or empty body
- **THEN** the poller SHALL insert a row with `status="unreachable"`, `error_kind="http_error"`, and `body_status=null`
- **AND** it SHALL trigger an alert because the service is not providing actionable health information

#### Scenario: HTTP timeout classifies as unreachable with elapsed_ms

- **WHEN** the HTTP request exceeds `timeout_seconds` (default 5–15s per service)
- **THEN** the poller SHALL insert a row with `status="unreachable"`, `error_kind="timeout"`, `detail="exceeded Ns timeout"`, and the actual `elapsed_ms` at the moment of timeout
- **AND** `response_time_ms` SHALL be the same `elapsed_ms` so dashboards can graph latency-cap-hit frequency

#### Scenario: Connection error classifies as unreachable with diagnostic detail

- **WHEN** httpx raises `HTTPError` (connect refused, DNS failure, TLS error)
- **THEN** the poller SHALL insert a row with `status="unreachable"`, `error_kind="connection_error"`, `detail=<exception class name + message>`
- **AND** the `elapsed_ms` SHALL be the wall-clock time spent on the failed request

The `payload` JSON column SHALL always include `error_kind` when the snapshot is not a clean 200 response, enabling dashboards to group unreachable events by failure mode (timeout vs http_error vs connection_error) rather than treating them as a single category.

Dedicated columns extracted per service:

| Service          | Columns extracted from payload                                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------ |
| webhook-receiver | `dbos_connected` ← `payload["scheduler"]["dbos_connected"]`                                                              |
| ai-review        | `dbos_connected` ← `payload["scheduler"]["dbos_connected"]`, `schedule_count` ← `payload["scheduler"]["schedule_count"]` |
| tdt-scheduler    | `dbos_connected` ← `payload["dbos_connected"]`, `schedule_count` ← `payload["schedule_count"]`                           |

#### Scenario: Records webhook-receiver healthy snapshot

- **WHEN** webhook-receiver returns HTTP 200 with `status: "healthy"` and all checks pass
- **THEN** the poller SHALL insert a row with `status="healthy"`, `dbos_connected=BOOLEAN`, and the full payload JSON

#### Scenario: Records ai-review degraded snapshot from sub-check warning

- **WHEN** ai-review returns HTTP 200 with `checks.reviewer_probes.status="warning"`
- **THEN** the poller SHALL insert a row with `status="degraded"` and SHALL trigger an alert

#### Scenario: Records tdt-scheduler unreachable when Docker container is down

- **WHEN** the request to `localhost:9100/scheduler/health` raises `httpx.ConnectError`
- **THEN** the poller SHALL insert a row with `status="unreachable"` and SHALL trigger an alert

### Requirement: Alert Events Emitted on State Transitions with Flap Suppression

The health poller SHALL emit alert events when a service transitions between health states (healthy → degraded, healthy → unreachable, degraded → healthy, etc.). Alert events SHALL be stored in the `health_alerts` table.

The poller SHALL implement flap suppression: when a service transitions between states multiple times within a 60-second window, only the first transition SHALL emit an alert. Subsequent transitions within the window SHALL be silently recorded in the snapshots table but SHALL NOT create new alert records.

Alert records SHALL contain: `timestamp`, `service_name`, `from_state`, `to_state`, `duration_seconds` (seconds since the last state change).

#### Scenario: Transition to unreachable triggers alert with duration

- **WHEN** webhook-receiver was healthy and now returns `unreachable`
- **THEN** the poller SHALL insert an alert with `from_state="healthy"`, `to_state="unreachable"`, and `duration_seconds` equal to the elapsed time since the last snapshot with a different status

#### Scenario: Recovery triggers resolved alert

- **WHEN** ai-review was degraded and now returns `healthy`
- **THEN** the poller SHALL insert an alert with `from_state="degraded"`, `to_state="healthy"`, and `duration_seconds` equal to the outage duration

#### Scenario: Rapid flapping suppressed within 60-second window

- **WHEN** webhook-receiver transitions: healthy → unreachable → healthy → unreachable within 55 seconds
- **THEN** the poller SHALL emit exactly one alert (the first transition) and SHALL silently record the subsequent transitions in snapshots

### Requirement: DuckDB Tables Created with Proper Schema

The store SHALL create these tables on first run using `IF NOT EXISTS`:

```sql
CREATE TABLE health_snapshots (
  timestamp TIMESTAMP NOT NULL,
  service_name VARCHAR NOT NULL,
  status VARCHAR NOT NULL CHECK (status IN ('healthy', 'degraded', 'unreachable')),
  response_time_ms INTEGER,
  dbos_connected BOOLEAN,
  schedule_count INTEGER,
  payload JSON
);

CREATE TABLE health_alerts (
  timestamp TIMESTAMP NOT NULL,
  service_name VARCHAR NOT NULL,
  from_state VARCHAR NOT NULL,
  to_state VARCHAR NOT NULL,
  duration_seconds INTEGER
);

CREATE INDEX idx_snapshots_time_service ON health_snapshots(timestamp, service_name);
CREATE INDEX idx_alerts_time_service ON health_alerts(timestamp, service_name);
```

#### Scenario: Tables created idempotently on first run

- **WHEN** `DuckDBStore.init_db()` is called for the first time on a new database file
- **THEN** it SHALL create `health_snapshots` and `health_alerts` tables and their indexes
- **AND** subsequent calls SHALL succeed without error (tables already exist)

### Requirement: Background Process with Lifecycle Management

The health poller SHALL run as a background daemon process. It SHALL handle SIGTERM and SIGINT gracefully, completing the current poll cycle before exiting. The process SHALL write its PID to `~/.tdt/observability/health-poller.pid` on start and remove the file on clean exit.

#### Scenario: Clean shutdown on SIGTERM flushes final state

- **WHEN** the poller receives SIGTERM during an active poll cycle
- **THEN** it SHALL complete that cycle, flush pending alerts, close the DuckDB connection, delete the PID file, and exit with code 0

#### Scenario: PID file prevents duplicate instance

- **WHEN** the poller starts and `~/.tdt/observability/health-poller.pid` already exists
- **THEN** it SHALL check whether the PID is still running; if running, it SHALL exit with code 1; if not running, it SHALL overwrite the stale file

### Requirement: Timezone-Safe Datetime Arithmetic at the Store Boundary

The store and poller SHALL treat all timestamps that flow across their public APIs as UTC-aware `datetime` objects. DuckDB stores and returns `TIMESTAMP` columns as **offset-naive** `datetime` objects (the database has no native timezone concept; values are UTC by convention). Subtracting an offset-naive `datetime` from an offset-aware one (e.g. `datetime.now(UTC)`) raises `TypeError: can't subtract offset-naive and offset-aware datetimes` and crashes the caller.

To prevent this class of bug from recurring across the boundary, the store SHALL expose a helper `_ensure_utc_aware(ts)` that attaches `UTC` to any naive `datetime` it returns. Every store method that surfaces a timestamp to the poller (e.g. `get_last_alert_timestamp`) SHALL route the value through this helper. The poller SHALL additionally belt-and-braces normalise any locally-tracked timestamp (e.g. `self._last_transition_time`) before subtracting it from `datetime.now(UTC)`, so a future store-side refactor cannot silently re-introduce the bug.

#### Scenario: DuckDB-naive timestamp is normalised to UTC-aware

- **WHEN** `DuckDBStore.get_last_alert_timestamp` reads a `TIMESTAMP` column from `health_alerts`
- **THEN** it SHALL return an offset-aware `datetime` (with `tzinfo=UTC`)
- **AND** subtracting that value from `datetime.now(UTC)` SHALL NOT raise

#### Scenario: Poller guards against locally-tracked naive timestamps

- **WHEN** `_poll_once` computes `duration_seconds = (now - last_transition).total_seconds()` or compares `now - last_alert_ts`
- **THEN** both operands SHALL be offset-aware before the subtraction
- **AND** the subtraction SHALL NOT raise even if `last_transition` was restored from a future snapshot/serialisation path that produced a naive `datetime`
