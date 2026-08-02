# Implementation Tasks — tdt-observability-dashboard

This document contains all implementation tasks for the three-phase observability dashboard.
Tasks are organized by phase and ordered by dependency. Each checkbox is independently verifiable.

---

## Phase 1: Health Aggregator + Streamlit Dashboard

### 1. Repository Setup

- [x] 1.1 Create `~/Developer/tdt/tdt-observability/` directory
- [x] 1.2 Create `pyproject.toml` with `hatchling` build, dependencies:
      `streamlit>=1.58.0`, `duckdb>=1.5.4`, `pydantic>=2.13.4`, `httpx>=0.28.0`, `structlog>=26.1.0`
      dev deps: `ruff>=0.15.0`, `mypy>=1.14.0`, `pytest>=9.0.0`
- [x] 1.3 Create `src/tdt_observability/__init__.py` with `__version__` and package metadata
- [x] 1.4 Create `src/tdt_observability/cli.py` with entry points: `health-poller` and `dashboard`
- [x] 1.5 Create `~/.tdt/observability/` directory structure:
      ```
      ~/.tdt/observability/
        config.yaml          # service endpoints
        log-sources.yaml     # log file patterns
        health.duckdb        # created by store.py
        health-poller.pid
        log-aggregator.pid
      ```
- [x] 1.6 Create `~/.tdt/observability/config.yaml` with default services:
      ```yaml
      services:
        - name: webhook-receiver
          url: http://localhost:8080/health
        - name: ai-review
          url: http://localhost:8090/health/full
        - name: tdt-scheduler
          url: http://localhost:9100/scheduler/health
      ```
- [x] 1.7 Verify: `cd ~/Developer/tdt/tdt-observability && uv sync && ruff check src/ && mypy src/ --strict`

### 2. DuckDB Store — Health Schema

- [x] 2.1 Create `src/tdt_observability/store.py` with `DuckDBStore` class
- [x] 2.2 Implement `init_db()` — creates tables with `IF NOT EXISTS`:
      ```sql
      CREATE TABLE health_snapshots (
        id BIGINT AUTOINCREMENT PRIMARY KEY,
        timestamp TIMESTAMP,
        service_name VARCHAR,
        status VARCHAR,       -- 'healthy' | 'degraded' | 'unreachable'
        response_time_ms INTEGER,
        dbos_connected BOOLEAN,
        schedule_count INTEGER,
        payload JSON
      );
      CREATE INDEX idx_snapshots_time_service ON health_snapshots(timestamp, service_name);

      CREATE TABLE health_alerts (
        id BIGINT AUTOINCREMENT PRIMARY KEY,
        timestamp TIMESTAMP,
        service_name VARCHAR,
        from_state VARCHAR,
        to_state VARCHAR,
        duration_seconds INTEGER
      );
      ```
- [x] 2.3 Implement `insert_snapshot(service_name, status, response_time_ms, payload)` → `int` (row id)
- [x] 2.4 Implement `get_latest_snapshots()` → list of dicts, one per service (latest timestamp per service)
- [x] 2.5 Implement `get_health_trend(service_name, hours: int)` → list of (timestamp, status, response_time_ms)
- [x] 2.6 Implement `get_recent_alerts(limit: int = 100)` → list of alert dicts
- [x] 2.7 Implement `insert_alert(service_name, from_state, to_state, duration_seconds)`
- [x] 2.8 Verify: `pytest tests/test_store.py -v`

### 3. Health Poller

- [x] 3.1 Create `src/tdt_observability/health_poller.py` with `HealthPoller` class
- [x] 3.2 `_load_config()` — reads `~/.tdt/observability/config.yaml` via `yaml.safe_load`; returns hardcoded defaults if file absent (webhook-receiver@8080, ai-review@8090, tdt-scheduler@9100)
- [x] 3.3 `_derive_status(payload: dict, http_status: int)` → `'healthy' | 'degraded' | 'unreachable'`
      - `unreachable` if HTTP status != 200 or request exception
      - `degraded` if `payload.get("status")` in (`"degraded"`, `"unhealthy"`) or any sub-check has status `warning`/`degraded`
      - `healthy` otherwise
- [x] 3.4 `_extract_fields(payload: dict)` → `{dbos_connected: bool | None, schedule_count: int | None}`
      - Extracts `payload["scheduler"]["dbos_connected"]` and `payload["scheduler"]["schedule_count"]` from webhook-receiver/ai-review/scheduler payloads
- [x] 3.5 `_check_service(name, url)` → `(status, response_time_ms, payload)` using `httpx.get(url, timeout=5.0)`
- [x] 3.6 `_get_previous_status(name)` → last `status` from DuckDB for service, or `None`
- [x] 3.7 `_poll_once()` — loops all services, calls `_check_service`, inserts snapshot, computes state transition, emits alert if changed (with 60s flap suppression window)
- [x] 3.8 `_run_loop(interval: int = 30)` — asyncio or threading loop calling `_poll_once()` every `interval` seconds
- [x] 3.9 `_write_pid()` on start, `_remove_pid()` on exit; graceful SIGTERM/SIGINT handler
- [x] 3.10 Create `src/tdt_observability/health_poller/__main__.py` with CLI:
      `python -m tdt_observability.health_poller --interval 30`
- [x] 3.11 Verify: run poller for 2 minutes, check `~/.tdt/observability/health.duckdb` has rows

### 4. Streamlit Dashboard — Health Page

- [x] 4.1 Create `src/tdt_observability/dashboard/__init__.py`
- [x] 4.2 Create `src/tdt_observability/dashboard/app.py`:
      ```python
      st.set_page_config(title="TDT Observability", page_icon="🔍", layout="wide")
      ```
- [x] 4.3 Create `@st.cache_resource` for `DuckDBStore` with `on_release=lambda: None` (DuckDB doesn't need explicit close):
      ```python
      @st.cache_resource
      def get_store() -> DuckDBStore:
          store = DuckDBStore("~/.tdt/observability/health.duckdb")
          store.init_db()
          return store
      ```
- [x] 4.4 Create `src/tdt_observability/dashboard/pages/01_health.py`:
- [x] 4.5 Service health grid — `st.columns(n)` with one column per service:
      - Color-coded status badge: green `"Healthy"` / yellow `"Degraded"` / red `"Unreachable"`
      - Show last checked timestamp and response time
      - For webhook-receiver: circuit breaker status, debouncer status, `ai_review_dispatch` status from payload
      - For ai-review: scheduler `dbos_connected`, reviewer probe states
      - For tdt-scheduler: `dbos_connected`, `schedule_count`
- [x] 4.6 KPI metric cards using `st.metric`:
      - Total services monitored
      - Healthy / degraded / unreachable counts
      - Average response time (ms)
      - 24h alert count
- [x] 4.7 Health trend chart using `st.line_chart`:
      - Query: `SELECT timestamp, service_name, status FROM health_snapshots WHERE timestamp > now() - INTERVAL '1 hour'`
      - Map: `healthy=2, degraded=1, unreachable=0`
      - Time range selector: `st.radio` with options 1h/6h/24h/7d, updates chart query
- [x] 4.8 Alert history table using `st.dataframe`:
      - Columns: timestamp, service, from_state, to_state, duration_seconds
      - Filter by service_name
- [x] 4.9 Add auto-refresh: `st_autorefresh` widget or `st.empty()` + JavaScript `meta http-equiv="refresh"` in `app.py`
- [x] 4.10 Verify: `streamlit run src/tdt_observability/dashboard/app.py`, open localhost:8501, verify grid and chart render

### 5. Dashboard Navigation and Pages

- [x] 5.1 Create `src/tdt_observability/dashboard/pages/00_overview.py` — landing page with summary metrics and quick links
- [x] 5.2 Create `src/tdt_observability/dashboard/pages/02_logs.py` — stub page with `st.info("Log search — Phase 2")`
- [x] 5.3 Create `src/tdt_observability/dashboard/pages/03_slos.py` — stub page with `st.info("SLO dashboard — Phase 3")`
- [x] 5.4 Add sidebar with `st.navigation` and all page links
- [x] 5.5 Create `~/.tdt/observability/README.md` with:
      - Architecture overview
      - `streamlit run ~/Developer/tdt/tdt-observability/src/tdt_observability/dashboard/app.py`
      - `python -m tdt_observability.health_poller --interval 30`

### 6. Launchd Agent for Health Poller

- [x] 6.1 Create `~/Developer/tdt/tdt-observability/deploy/launchd/com.tdt.observability-health-poller.plist` following the existing TDT pattern (cf. `~/Developer/tdt/deployments/ai-review/launchd/com.tdt.ai-review.plist`):
      ```xml
      <key>ProgramArguments</key>
      <array>
          <string>/Users/lekhanhvinh/.tdt/venvs/tdt-observability/bin/python</string>
          <string>-m</string>
          <string>tdt_observability.health_poller</string>
          <string>--interval</string>
          <string>30</string>
      </array>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      <key>StandardOutPath</key>
      <string>/Users/lekhanhvinh/.tdt/logs/observability-health-poller.stdout.log</string>
      <key>StandardErrorPath</key>
      <string>/Users/lekhanhvinh/.tdt/logs/observability-health-poller.stderr.log</string>
      ```
- [x] 6.2 Document install: `ln -s ~/Developer/tdt/tdt-observability/deploy/launchd/com.tdt.observability-health-poller.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.tdt.observability-health-poller.plist`

---

## Phase 2: Log Aggregator

### 7. DuckDB Store — Events Schema

- [x] 7.1 Add to `src/tdt_observability/store.py` — extend `init_db()` with `events` table:
      ```sql
      CREATE TABLE events (
        id BIGINT AUTOINCREMENT PRIMARY KEY,
        timestamp TIMESTAMP,
        service VARCHAR,
        level VARCHAR,
        event_type VARCHAR,
        trace_id VARCHAR,
        message TEXT,
        extra JSON,
        ingest_timestamp TIMESTAMP DEFAULT NOW(),
        source_file VARCHAR
      );
      CREATE INDEX idx_events_time_service_level ON events(timestamp, service, level);
      CREATE INDEX idx_events_event_type ON events(event_type);
      CREATE INDEX idx_events_trace_id ON events(trace_id) WHERE trace_id IS NOT NULL;
      ```
- [x] 7.2 Implement `insert_events_batch(events: list[dict])` — batch insert in single transaction
- [x] 7.3 Implement `search_events(service=None, level=None, event_type=None, query=None, start_time=None, end_time=None, limit=100, offset=0)` → list of dicts
      - Builds SQL: `SELECT * FROM events WHERE ... ORDER BY timestamp DESC LIMIT ? OFFSET ?`
      - Uses `ILIKE` for free-text search on `message` and `extra`
- [x] 7.4 Implement `get_event_counts_by_service_and_level(start_time, end_time)` → list of (service, level, count)
- [x] 7.5 Implement `get_log_stats(start_time, end_time)` → dict with total_count, error_count, error_rate per service
- [x] 7.6 Verify: `pytest tests/test_store.py::test_events -v`

### 8. Log Collector

- [x] 8.1 Add `watchfiles>=1.2.0` to dependencies
- [x] 8.2 Create `src/tdt_observability/log_collector.py` with `LogCollector` class
- [x] 8.3 `_load_sources()` — reads `~/.tdt/observability/log-sources.yaml` or returns defaults:
      - `~/.tdt/logs/*.log` (exclude `*.1.log`, `*.2.log` rotated backups)
      - `~/.tdt/logs/jira-daily-reports/**/*.log`
- [x] 8.4 `_file_offset_tracker: dict[str, int]` — maps file path → last byte offset
- [x] 8.5 `_read_new_lines(path, offset)` — opens file, seeks to offset, reads all new lines, returns (lines, new_offset)
- [x] 8.6 `_parse_structlog(line: str)` → dict | None:
      - Attempts `json.loads(line)`, returns dict with `timestamp`, `level`, `logger`, `event`, `event_kwargs` if valid
      - Returns `None` if not valid JSON
- [x] 8.7 `_parse_text_line(line: str)` → dict | None:
      - Regex: `^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4})\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+(\S+)\s+(.*)$`
      - Returns dict with `timestamp`, `level`, `logger`, `message`, `event_type` from first word of message
- [x] 8.8 `_derive_service_name(logger: str)` → e.g., `jira_daily_reports.reports.sprint_report_sheet` → `jira-daily-reports`
- [x] 8.9 `_enrich(event: dict, source_file: str)` → adds `ingest_timestamp`, `source_file`, `service_name`, `event_type`
- [x] 8.10 `_batch: list[dict]` + `_last_flush: float` (time)
- [x] 8.11 `_flush_batch()` — calls `store.insert_events_batch(batch)`, resets batch, resets timer
- [x] 8.12 `_run_loop(debounce=1.0)`:
      - Calls `watchfiles.awatch(sources, debounce=debounce)` (async)
      - On each batch of changes, reads new lines from changed files
      - Calls `_flush_batch()` every 5s or when len(batch) >= 500
- [x] 8.13 Log rotation: compare file inode (`os.stat(path).st_ino`) before reading; reset offset to 0 if inode changed
- [x] 8.14 `_write_pid()` / `_remove_pid()` on start/exit
- [x] 8.15 Create `src/tdt_observability/log_collector/__main__.py` with CLI
- [x] 8.16 Verify: run collector for 2 minutes, check `events` table has rows from `~/.tdt/logs/jira-reports.log`

### 9. Streamlit Dashboard — Log Search Page

- [x] 9.1 Extend `src/tdt_observability/dashboard/pages/02_logs.py`:
- [x] 9.2 `@st.cache_data(ttl=30)` for distinct service list: `SELECT DISTINCT service FROM events ORDER BY service`
- [x] 9.3 Filter panel with `st.columns([1,1,1,2,2])`:
      - Service: `st.selectbox("Service", ["All"] + services)`
      - Level: `st.selectbox("Level", ["All", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])`
      - Event type: `st.selectbox("Event Type", ["All"] + event_types)` (from distinct values)
      - Time range: `st.date_input("From", value=date.today())` + `st.date_input("To")`
      - Query: `st.text_input("Search", placeholder="e.g. handoff_scheduled")`
- [x] 9.4 `st.button("Search")` triggers `st.cache_data` re-query
- [x] 9.5 Results `st.dataframe` with columns: timestamp, service, level, event_type, message (truncated to 200 chars)
- [x] 9.6 Row expansion: `st.expander("Details")` showing full JSON of `extra` field
- [x] 9.7 Pagination using `st.pagination` (Streamlit 1.58+) with 100 rows per page:
      ```python
      for page in st.pagination(total_pages, format_formatter=lambda x: f"Page {x}"):
          display_logs_page(page)
      ```
- [x] 9.8 Log distribution chart: `st.bar_chart` showing event count by service and level (from `get_event_counts_by_service_and_level`)
- [x] 9.9 Verify: search for ERROR events in last 24h, verify results display with expansion

### 10. Launchd Agent for Log Collector

- [x] 10.1 Create `~/Developer/tdt/tdt-observability/deploy/launchd/com.tdt.observability-log-aggregator.plist`
      (same pattern as health poller plist, pointing to `tdt_observability.log_collector`)
- [x] 10.2 Document install command

---

## Phase 3: OpenTelemetry Graduation

### 11. OTel Setup Module — webhook-receiver

- [x] 11.1 Add to `~/Developer/tdt/webhook-receiver/pyproject.toml` dependencies:
      ```
      opentelemetry-api>=1.43.0
      opentelemetry-sdk>=1.43.0
      opentelemetry-instrumentation-fastapi
      opentelemetry-instrumentation-httpx
      opentelemetry-exporter-otlp-http-protobuf
      ```
- [x] 11.2 Create `~/Developer/tdt/webhook-receiver/src/webhook_receiver/otel_setup.py`:
      ```python
      import os
      from opentelemetry import trace
      from opentelemetry.sdk.trace import TracerProvider
      from opentelemetry.sdk.trace.export import BatchSpanProcessor
      from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
      from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
      from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
      from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
      import structlog

      def setup_otel(service_name: str) -> None:
          if os.environ.get("OTEL_ENABLED") != "true":
              return
          resource = Resource.create({
              SERVICE_NAME: service_name,
              SERVICE_VERSION: "1.0.0",
              "deployment.environment": "local",
          })
          provider = TracerProvider(resource=resource)
          trace.set_tracer_provider(provider)
          otlp_exporter = OTLPSpanExporter(
              endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/traces"
          )
          provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

          # Inject trace context into structlog
          _inject_trace_context_into_structlog()

          # Auto-instrument FastAPI
          # (called from app.py after create_app())
      ```
- [x] 11.3 Implement `_inject_trace_context_into_structlog()`:
      ```python
      def _otlp_trace_context_processor(_, __, event_dict):
          span = trace.get_current_span()
          if span.is_recording():
              ctx = span.get_span_context()
              event_dict["trace_id"] = format(ctx.trace_id, "032x")
              event_dict["span_id"] = format(ctx.span_id, "016x")
          return event_dict
      ```
      Prepend `_otlp_trace_context_processor` to the existing processors list in `utils/logging.py` (only when `OTEL_ENABLED=true`).
- [x] 11.4 Modify `~/Developer/tdt/webhook-receiver/src/webhook_receiver/api/app.py`:
      - After `create_app()` returns: `from webhook_receiver.otel_setup import setup_otel; setup_otel("webhook-receiver")`
      - Then: `FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/health/ingress,/healthz")`
      - Then: `HTTPXClientInstrumentor().instrument()`
- [x] 11.5 Guard all OTel code behind `OTEL_ENABLED` env var — when absent, `setup_otel()` returns immediately
- [x] 11.6 Add to `webhook-receiver/.env.example`:
      ```
      # OpenTelemetry (optional)
      OTEL_ENABLED=false
      OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
      OTEL_SERVICE_NAME=webhook-receiver
      ```
- [x] 11.7 Verify: set `OTEL_ENABLED=true`, start LGTM, make a test webhook, check trace in Grafana at localhost:3000 → Explore → Tempo

### 12. OTel Setup Module — ai-review

- [x] 12.1 Add same OTel dependencies to `~/Developer/tdt/ai-review/pyproject.toml`
- [x] 12.2 Create `~/Developer/tdt/ai-review/src/ai_review/otel_setup.py` — identical pattern to webhook-receiver with `setup_otel("ai-review")`
- [x] 12.3 Find `ai-review`'s logging setup (imports from `tdt_core.scheduler` or uses `structlog.get_logger(__name__)` directly in `api/app.py`) — add same trace context processor injection
- [x] 12.4 Find FastAPI `create_app()` in `ai-review/src/ai_review/api/app.py` and add same three OTel calls after app creation
- [x] 12.5 Guard all OTel code behind `OTEL_ENABLED` env var
- [x] 12.6 Add same env vars to `ai-review/.env.example`
- [x] 12.7 Verify: run both services with `OTEL_ENABLED=true`, send a webhook, verify distributed trace spans for both services in Grafana Tempo

### 13. Grafana LGTM Setup and Dashboards

- [x] 13.1 Create `~/Developer/tdt/tdt-observability/deploy/lgtm/run-lgtm.sh`:
      ```bash
      #!/bin/bash
      set -e
      mkdir -p ~/.tdt/observability/lgtm-data
      docker pull grafana/otel-lgtm:v0.28.0
      docker run -d --name tdt-otel-lgtm \
        -p 3000:3000 -p 4317:4317 -p 4318:4318 \
        -v ~/.tdt/observability/lgtm-data:/data \
        grafana/otel-lgtm:v0.28.0
      echo "Grafana: http://localhost:3000 (admin/admin)"
      ```
- [x] 13.2 Create `~/Developer/tdt/tdt-observability/grafana/provisioning/datasources/datasources.yaml`:
      ```yaml
      apiVersion: 1
      datasources:
        - name: Tempo
          type: tempo
          access: proxy
          url: http://localhost:3200
        - name: Loki
          type: loki
          access: proxy
          url: http://localhost:3100
        - name: Mimir
          type: prometheus
          access: proxy
          url: http://localhost:9009
      ```
- [x] 13.3 Create `~/Developer/tdt/tdt-observability/grafana/provisioning/dashboards/dashboards.yaml`:
      ```yaml
      apiVersion: 1
      providers:
        - name: TDT Observability
          orgId: 1
          folder: TDT
          type: file
          options:
            path: /etc/grafana/provisioning/dashboards
      ```
- [x] 13.4 Create `~/Developer/tdt/tdt-observability/grafana/dashboards/tdt-service-health.json` — Grafana dashboard JSON:
      - Panel 1: Service health status grid (from Mimir metrics)
      - Panel 2: Response time heatmap
      - Panel 3: Error rate by service
- [x] 13.5 Create `~/Developer/tdt/tdt-observability/grafana/dashboards/tdt-distributed-traces.json`:
      - Tempo search panel
      - Trace detail panel with span list
      - Service graph (Grafana 13+ node graph)
      - Loki log panel linked by trace_id
- [x] 13.6 Update `run-lgtm.sh` to mount provisioning dirs:
      ```bash
      docker run -d --name tdt-otel-lgtm \
        -p 3000:3000 -p 4317:4317 -p 4318:4318 \
        -v ~/.tdt/observability/lgtm-data:/data \
        -v ~/Developer/tdt/tdt-observability/grafana/provisioning:/etc/grafana/provisioning \
        -v ~/Developer/tdt/tdt-observability/grafana/dashboards:/etc/grafana/provisioning/dashboards \
        grafana/otel-lgtm:v0.28.0
      ```

### 14. SLO Definitions and Burn-Rate Alerts

- [x] 14.1 Add `mizcausevic-dev/slo-budget-tracker` to `tdt-observability` dependencies (or implement inline):
      ```python
      # src/tdt_observability/slo_tracker.py
      from dataclasses import dataclass
      from datetime import datetime, timedelta, timezone

      @dataclass(frozen=True)
      class SLODefinition:
          name: str
          target: float          # e.g. 0.995 for 99.5%
          window_days: int = 30
          fast_burn_windows: tuple[int, int] = (3600, 21600)  # 1h, 6h
          slow_burn_windows: tuple[int, int] = (21600, 259200)  # 6h, 3d
          fast_burn_threshold: float = 14.4
          slow_burn_threshold: float = 3.0
      ```
- [x] 14.2 Define SLO-1: `SLODefinition(name="webhook-delivery", target=0.995, ...)`
      - Query from events table: `event_type IN ('handoff_dispatch_accepted', 'handoff_dispatch_failed')`
- [x] 14.3 Define SLO-2: `SLODefinition(name="review-latency", target=0.950, ...)`
      - Query: `event_type='orchestration_completed'` with elapsed time from corresponding `intake_received`
- [x] 14.4 Define SLO-3: `SLODefinition(name="scheduler-connectivity", target=0.999, ...)`
      - Query from health_snapshots: `dbos_connected IS TRUE / total_checks`
- [x] 14.5 Implement `compute_burn_rate(slo, window_seconds)`:
      ```python
      def compute_burn_rate(slo: SLODefinition, window_seconds: int) -> float:
          total = total_requests_in_window(window_seconds)
          failures = failures_in_window(window_seconds)
          error_rate = failures / total if total > 0 else 0
          allowed_error_rate = 1 - slo.target
          window_fraction = window_seconds / (slo.window_days * 86400)
          return error_rate / (allowed_error_rate * window_fraction) if allowed_error_rate > 0 else 0
      ```
- [x] 14.6 Implement `check_burn_rates()` → list of `BurnRateAlert`:
      - Fast burn: `compute_burn_rate(1h) >= 14.4 AND compute_burn_rate(6h) >= 14.4` → critical
      - Slow burn: `compute_burn_rate(6h) >= 3.0 AND compute_burn_rate(3d) >= 3.0` → warning
- [x] 14.7 Extend `src/tdt_observability/dashboard/pages/03_slos.py`:
      - SLO gauge cards using `st.metric`: ratio %, remaining budget %, burn rate
      - Color-coded: green < 50% budget used, yellow 50-80%, red > 80%
      - Estimated exhaustion date from burn rate
- [x] 14.8 Implement `emit_weekly_summary()`: queries all SLO snapshots, emits `event="slo_weekly_summary"` log
- [x] 14.9 Verify: seed mock data, compute burn rates, verify calculations match expected values

### 15. Error Tracking (Optional)

- [x] 15.1 Document `errex` in `tdt-observability/README.md` as optional:
      ```bash
      curl -fsSL https://errex.sh | sh
      ./errex --dsn http://localhost:8080 --port 8080
      ```
- [x] 15.2 Add `sentry-sdk` integration guide for webhook-receiver and ai-review:
      ```python
      import sentry_sdk
      sentry_sdk.init(dsn="http://localhost:8080@localhost:8080/1")
      ```
- [x] 15.3 Note: This step is OPTIONAL — only if operators want centralized error tracking beyond DuckDB

---

## Verification and Documentation

- [x] V.1 `cd ~/Developer/tdt/tdt-observability && ruff check src/ --fix && ruff format src/`
- [x] V.2 `cd ~/Developer/tdt/tdt-observability && mypy src/ --strict`
- [x] V.3 `cd ~/Developer/tdt/tdt-observability && pytest tests/ -v`
- [x] V.4 `openspec validate --strict tdt-observability-dashboard`
- [x] V.5 Update `tdt-observability/README.md`:
      - Architecture diagram (ASCII)
      - Directory layout: `~/.tdt/observability/`, `src/tdt_observability/`, `deploy/`
      - Run commands for Phase 1, Phase 2, Phase 3
      - Env vars reference: `OTEL_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `TDT_OBSERVABILITY_PORT`
      - Retention policy: 30 days for logs, 90 days for health snapshots
- [x] V.6 Commit in two steps:
      - Commit 1: `tdt-meta/openspec/changes/tdt-observability-dashboard/` (OpenSpec artifacts)
      - Commit 2: `tdt-observability/` (new repo)
- [x] V.7 Run `npx gitnexus analyze` in `~/Developer/tdt/` to refresh index
- [x] V.8 Run `npx gitnexus detect_changes` in `tdt-observability/` to verify scope
