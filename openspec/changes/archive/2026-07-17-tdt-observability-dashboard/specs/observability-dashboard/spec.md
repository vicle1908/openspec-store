# observability-dashboard

## ADDED Requirements

### Requirement: Service Health Grid with TDT-Specific Status Display

The dashboard SHALL display a service health grid using `st.columns()`. Each service card SHALL show:

- Color-coded status badge: green for `healthy`, yellow for `degraded`, red for `unreachable`
- Last checked timestamp
- Response time in milliseconds
- For `unreachable` snapshots, a diagnostic caption showing the failure kind from the payload's `error_kind` (`timeout`, `http_error`, `connection_error`), the `detail` field (e.g. `"exceeded 5s timeout"`, `"HTTP 503"`), and the service's self-reported `body_status` if the response body was parseable
- Service-specific health indicators from the payload JSON:

| Service          | Specific indicators shown                                                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| webhook-receiver | circuit breaker state (`checks.circuit_breaker.status`), debouncer state (`debouncer.enabled`), `ai_review_dispatch` status                                      |
| ai-review        | `scheduler.dbos_connected` (prominent), reviewer probe states (`checks.reviewer_probes.reviewers.kimi.status`, `checks.reviewer_probes.reviewers.claude.status`) |
| tdt-scheduler    | `dbos_connected` (prominent), `schedule_count`, `scheduling_enabled`                                                                                             |

The grid SHALL auto-refresh using `st.cache_data(ttl=30)` to cache DuckDB queries.

#### Scenario: Displays circuit breaker degradation for webhook-receiver

- **WHEN** webhook-receiver's `checks.circuit_breaker.status` is `"degraded"`
- **THEN** the service card SHALL display a yellow status badge with the text "Degraded — circuit_breaker"

#### Scenario: Displays dbos_connected false for tdt-scheduler

- **WHEN** the tdt-scheduler snapshot has `dbos_connected=false`
- **THEN** the service card SHALL display a red status badge with "Unreachable" and `schedule_count=0`

#### Scenario: Surfaces error_kind diagnostic on unreachable events

- **WHEN** a snapshot has `status="unreachable"` and `payload.error_kind` is set
- **THEN** the service card SHALL render a caption with the error kind, detail, and (for HTTP errors) the body status, e.g. `Failure: error_kind=http_error | detail=HTTP 503 | body_status=degraded`
- **AND** the caption SHALL NOT appear on `healthy` or `degraded` snapshots (which have no error_kind populated)

### Requirement: Health Trend Chart with Configurable Time Range

The dashboard SHALL display a time-series chart showing health status over a user-selectable time range. The range selector SHALL offer four options via `st.radio`: 1 hour (default), 6 hours, 24 hours, 7 days.

The chart SHALL map status values to numeric integers for line plotting: `healthy=2`, `degraded=1`, `unreachable=0`. The query SHALL be: `SELECT timestamp, service_name, status FROM health_snapshots WHERE timestamp > NOW() - INTERVAL 'N hours'`.

#### Scenario: Shows 6-hour trend when selected

- **WHEN** the user selects "6 hours"
- **THEN** the chart SHALL re-query DuckDB and re-render a line chart for the last 6 hours

#### Scenario: Disconnected line for unreachable periods

- **WHEN** tdt-scheduler was unreachable from 10:00 to 10:15
- **THEN** the chart SHALL show a gap in the line during that period rather than interpolating between 9:59 and 10:16

### Requirement: Log Search with Faceted Filtering and Pagination

The dashboard SHALL provide a log search interface with filters for: `service_name`, `level`, `event_type`, `time_range`, and free-text `query`. The search SHALL use `st.cache_data(ttl=60)` to cache results.

Results SHALL be displayed using `st.dataframe` with columns: `timestamp`, `service`, `level`, `event_type`, `message` (truncated to 200 characters). Pagination SHALL use `st.number_input` with 100 rows per page. The total result count is unknown upfront without an expensive COUNT query, so numbered page buttons (`st.pagination`) are not used.

#### Scenario: Filters by service and ERROR level

- **WHEN** the user selects `service="webhook-receiver"` and `level="ERROR"`
- **THEN** the search SHALL query `WHERE service='webhook-receiver' AND level='ERROR' ORDER BY timestamp DESC`

#### Scenario: Free-text search uses ILIKE

- **WHEN** the user enters `query="circuit_breaker"`
- **THEN** the search SHALL use `WHERE message ILIKE '%circuit_breaker%' OR extra ILIKE '%circuit_breaker%'`

#### Scenario: Pagination navigates through results

- **WHEN** the search returns 350 results
- **THEN** `st.pagination` SHALL show pages 1–4, and clicking page 3 SHALL display rows 201–300

#### Scenario: Clicking a row expands full event JSON

- **WHEN** the user clicks a row
- **THEN** an `st.expander` SHALL show the full `extra` JSON and `message` fields via `st.json`

### Requirement: KPI Metric Cards Using st.metric

The dashboard SHALL display KPI metric cards at the top of the overview page:

- Total services monitored
- Count: `healthy`, `degraded`, `unreachable`
- Average response time across all services (ms)
- Alert count in the last 24 hours

Each metric SHALL use `st.metric` with a delta indicator comparing to the previous period.

#### Scenario: Displays uptime percentage with delta

- **WHEN** the dashboard loads and 4 out of 5 services are healthy
- **THEN** the metric card SHALL display `80% healthy` with a delta showing the change from the previous check

### Requirement: Alert History Timeline

The dashboard SHALL display a timeline of `health_alerts` sorted by `timestamp DESC`, limited to the 100 most recent. Each row SHALL show: `timestamp`, `service_name`, `from_state` → `to_state`, and `duration_seconds`. A `st.selectbox` filter SHALL allow filtering by service.

#### Scenario: Shows recent alert from webhook-receiver

- **WHEN** webhook-receiver transitioned from healthy to degraded at 10:00
- **THEN** the timeline SHALL display a row: `2026-07-03 10:00:00 | webhook-receiver | healthy → degraded | 180s`

### Requirement: DuckDB Connection Managed via cache_resource

The dashboard SHALL use `st.cache_resource(on_release=lambda: conn.close())` to manage the DuckDB connection. The resource SHALL be instantiated once per Streamlit session and reused across all pages.

#### Scenario: Connection closed on Streamlit exit

- **WHEN** the Streamlit process receives SIGTERM
- **THEN** the `on_release` callback SHALL close the DuckDB connection cleanly
