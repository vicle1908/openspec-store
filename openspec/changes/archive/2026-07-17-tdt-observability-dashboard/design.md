## Context

The TDT ecosystem spans multiple Python services (webhook-receiver, ai-review, jira-daily-reports, scheduler) running as Docker containers, FastAPI processes, and launchd agents. Currently, each service exposes a `/health` endpoint and writes structured JSON logs to `~/.tdt/logs/` and `deployments/*/logs/`. There is no centralized view of system health, log search, or distributed tracing.

Operators diagnose issues by manually checking each service's health endpoint, grepping log files across directories, and correlating events by timestamp. This is slow, error-prone, and does not scale as the ecosystem grows.

## Goals / Non-Goals

**Goals:**

- Provide a single pane of glass for TDT ecosystem health (up/down, circuit breaker state, debouncer status, DBOS connectivity).
- Enable fast log search across all services from a single UI, with faceted filtering by service, level, event_type, and time range.
- Store health snapshots and log events in DuckDB for fast OLAP queries (10-200x faster than SQLite for aggregations).
- Add OpenTelemetry tracing to webhook-receiver and ai-review with trace context propagated into structlog, exportable to Grafana LGTM.
- Define SLOs for webhook delivery reliability, review latency, and scheduler availability, with burn-rate alerting.

**Non-Goals:**

- This change does NOT migrate existing data or services to new infrastructure.
- It does NOT add authentication to the Streamlit dashboard (local-only access on `localhost`).
- It does NOT replace existing structured logging — existing `structlog` output formats are preserved.
- It does NOT add OTel instrumentation by default — instrumentation is behind a feature flag (`OTEL_ENABLED=true`).
- It does NOT deploy Grafana LGTM in production — Phase 3 is for local development and testing only.

## Decisions

### Decision 1: DuckDB over SQLite for Analytics

**Choice:** DuckDB v1.5.4 (Variegata) for health snapshots and log event storage.

**Rationale:** Benchmark data shows DuckDB is 10-200x faster than SQLite for analytical queries (GROUP BY, SUM, window functions) on datasets of 1M+ rows. At current TDT log volumes, DuckDB's columnar storage and vectorized execution provide immediate performance benefits. The single-file, embedded, zero-server model is preserved — no new infrastructure.

**Alternative considered:** SQLite — rejected because dashboard aggregation queries (error rates over time, event counts by service, health trend) would be unacceptably slow at scale.

**Migration path:** DuckDB 2.0 (planned Fall 2026) will stabilize the Quack protocol for multi-process write access. The Phase 2 schema is designed to be Quack-compatible from the start.

### Decision 2: Streamlit over Grafana for Local Dashboard

**Choice:** Streamlit 1.58.0 for the primary dashboard UI.

**Rationale:** Streamlit is Python-native, integrates directly with DuckDB queries, and is fast to develop. The new `parallel=True` fragment mode (1.58.0) enables non-blocking health polling without full-script reruns. `st.cache_resource` with `on_release` ensures DuckDB connections are cleaned up properly.

**Alternative considered:** Grafana + Loki — rejected for Phase 1 because Grafana requires a Loki data source (adding Docker complexity), while Streamlit can query DuckDB directly with no additional services. Phase 3 adds Grafana via the LGTM stack for OTel-native dashboards.

### Decision 3: watchfiles over polling for Log Tailing

**Choice:** watchfiles v1.2.0 for log file monitoring.

**Rationale:** watchfiles uses OS-native APIs (inotify on Linux, FSEvents on macOS) for efficient event-based file watching. It is Rust-backed, battle-tested (used by uvicorn `--reload`), and has built-in debouncing at the Rust level. The async API (`awatch`) integrates cleanly with an asyncio-based collector.

**Alternative considered:** `tail -F` + shell pipeline — rejected because it is not Python-native and would require a separate process. watchdog — rejected because watchfiles is lighter and uvicorn's choice.

### Decision 4: OTel Instrumentation Behind Feature Flag

**Choice:** OTel tracing in webhook-receiver and ai-review is disabled by default (`OTEL_ENABLED=false`).

**Rationale:** Adding OTel to existing services introduces a new dependency and changes the logging pipeline. Making it opt-in via `OTEL_ENABLED` ensures zero risk to existing production services. Operators can enable it locally for development and testing.

**Trade-off:** The OTel collector URL and service name must be configured via environment variables when enabled.

### Decision 5: grafana/otel-lgtm for Local OTel Backend

**Choice:** Single Docker image `grafana/otel-lgtm:v0.28.0` for Phase 3 local OTel backend.

**Rationale:** LGTM bundles Grafana, Loki (logs), Tempo (traces), and Mimir (metrics) in a single image with sensible defaults. No configuration files needed — one `docker run` command. The image is actively maintained (66 releases, last push July 2, 2026). Cosign signatures available for verification.

**Alternative considered:** Manual Docker Compose with separate containers — rejected because LGTM provides the same stack with zero config overhead. Production deployment would use the same OTel instrumentation exporting to Grafana Cloud or self-hosted OTel Collector.

### Decision 6: Three-Phase Implementation

**Choice:** Implement in three incremental phases.

**Rationale:** A phased approach delivers value early without over-engineering:

- **Phase 1 (Health Aggregator):** Immediate value — see all service health at a glance. ~2-3 days.
- **Phase 2 (Log Aggregator):** Investigate — search logs, correlate events. ~3-4 days.
- **Phase 3 (OTel Graduation):** Scale — distributed tracing, Grafana dashboards, SLOs. ~5-7 days.

Each phase adds value independently. Phase 3 OTel instrumentation can be adopted incrementally per service.

### Decision 7: OTel Structlog Enrichment is Additive (Not a Breaking Change)

**Choice:** The structlog trace context processor is prepended to the existing processor chain in Phase 3, only when `OTEL_ENABLED=true`.

**Rationale:** The existing `webhook-ai-review-repo-split` and `ai-review-deployment-state` specs mandate a `X-Trace-Id` header (format: `trace-{uuid.hex[:12]}`) on the dispatch call and `trace_id` in the webhook response body. The OTel `traceparent` header (W3C format: `00-<32-hex>-<16-hex>-01`) is propagated via HTTPX auto-instrumentation and is **additive** — it does not replace, modify, or interfere with the legacy `X-Trace-Id` header. Structlog events gain `trace_id` and `span_id` extra fields only when an OTel span is active. When `OTEL_ENABLED=false`, the system is unchanged.

**Trade-off:** This means two trace correlation systems coexist in Phase 3 (legacy `X-Trace-Id` + OTel `traceparent`). This is intentional — it maintains backward compatibility with any tooling that depends on the legacy trace ID while enabling full distributed tracing.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| OTel adds `traceparent` header alongside existing `X-Trace-Id` (two trace ID systems coexist) | The existing `X-Trace-Id` and `trace_id` response field are unchanged; `traceparent` is additive and does not replace any behavior |
| Adding `traceparent` modifies `webhook-ai-review-repo-split` and `ai-review-deployment-state` contracts | The change is documented as a MODIFIED capability in proposal.md; the delta is additive (no behavior removed) |
| DuckDB write contention if multiple processes tail logs simultaneously | Log collector runs as a single background process; all services write to their own log files only |
| OTel Logs API is "Development" status, not yet stable | Phase 2 log aggregation uses native structlog JSON; OTel integration in Phase 3 focuses on traces (stable) and metrics (stable) |
| Streamlit dashboard requires port 8501 | Use `streamlit run --server.port 8501` with `TDT_OBSERVABILITY_PORT` env var; note in README |
| watchfiles on macOS FSEvents may miss rapid log writes | watchfiles debounce=1.0 (1 second) batches changes; acceptable for log aggregation |
| Grafana LGTM Docker image not suitable for production | Phase 3 explicitly targets local dev; production uses OTel instrumentation exporting to Grafana Cloud |
| DuckDB v2.0 breaking changes in Fall 2026 | Design schema to be compatible with both v1.5.x and v2.0; defer Quack protocol adoption until v2.0 stabilizes |
| Deployment modifying existing webhook-receiver and ai-review | All OTel changes guarded behind `OTEL_ENABLED` env var; disabled by default, no effect on existing deployments |

## Migration Plan

### Phase 1: Health Aggregator + Streamlit Dashboard

1. Create `tdt-observability/` repository with `pyproject.toml`.
2. Implement `health_poller.py` — polls `/health` endpoints every 30s.
3. Implement `store.py` — DuckDB schema for health snapshots.
4. Implement `dashboard.py` — Streamlit UI with service health grid.
5. Test: run Streamlit dashboard, verify health polling and display.
6. Document: `README.md` with run instructions, `~/.tdt/observability/` layout.

### Phase 2: Log Aggregator

1. Implement `log_collector.py` — uses watchfiles to tail log files.
2. Implement `log_parser.py` — parses structlog JSON lines.
3. Extend DuckDB schema with `events` table.
4. Extend Streamlit dashboard with log search page.
5. Test: tail existing log files, verify events appear in dashboard.

### Phase 3: OpenTelemetry Graduation

1. Add OTel dependencies to `webhook-receiver/pyproject.toml` and `ai-review/pyproject.toml`.
2. Implement trace context processor in structlog config (behind `OTEL_ENABLED`).
3. Add `FastAPIInstrumentor.instrument_app()` call with proper ordering.
4. Add `HTTPXClientInstrumentor().instrument()` for outbound tracing.
5. Write Grafana provisioning files for LGTM dashboard.
6. Define SLOs with burn-rate alert rules.
7. Test: enable OTel locally, verify traces appear in Grafana.

**Rollback:** Each phase is independent. Disabling the log collector stops log ingestion. Removing OTel environment variables reverts tracing. The DuckDB file can be deleted to reset state.

## Open Questions

1. **Retention policy:** How long should health snapshots and log events be retained in DuckDB? (Default suggestion: 30 days for logs, 90 days for health snapshots.)
2. **Log file locations:** Confirm all log file paths from `~/.tdt/logs/` and `deployments/*/logs/`.
3. **Service discovery:** Should the health poller auto-discover services from a config file, or use a hardcoded list for now?
4. **Grafana provisioning:** Should dashboards be committed as JSON files in the repo, or created manually in Grafana?
