## Why

The TDT ecosystem currently lacks centralized observability. Operators must check multiple health endpoints, grep log files across different directories, and piece together the state of the system from fragmented sources. This makes incident diagnosis slow and error-prone. A unified observability dashboard provides a single pane of glass for service health, log search, and eventually distributed tracing.

## What Changes

This change introduces a new `tdt-observability` repository providing:

- **Health Aggregator**: Polls `/health` endpoints from all TDT services (webhook-receiver, ai-review, scheduler) every 30 seconds, stores snapshots in DuckDB, and surfaces real-time status in a Streamlit dashboard.
- **Log Aggregator**: A background collector that tails existing structlog files from `~/.tdt/logs/` and deployment log directories, parses JSON log lines, and stores them in DuckDB for fast search.
- **Streamlit Dashboard**: A local-first web UI showing service health grid, health trend charts, log search with filtering, and alert history.
- **DuckDB Analytics Backend**: Fast OLAP queries (10-200x faster than SQLite for aggregations) on health snapshots and log events, stored in `~/.tdt/observability/`.
- **OpenTelemetry Instrumentation (Phase 3)**: Adds OTel tracing to existing services (webhook-receiver, ai-review) with trace context propagated into structlog. Exports to a local Grafana LGTM stack (Grafana + Loki + Tempo + Mimir in a single Docker image).
- **Error Tracking (Optional Phase 3)**: Integration with `errex` (7MB single-binary, SQLite-backed Sentry-compatible error tracker) as a lightweight alternative to full Sentry.

## Capabilities

### New Capabilities

- `observability-health-poller`: Continuously polls health endpoints of all TDT ecosystem services, records snapshots with timestamps, and tracks uptime/downtime windows.
- `observability-log-aggregator`: Tails structlog JSON files from all log sources, normalizes event metadata (service, level, event_type, trace_id), and batch-inserts into DuckDB.
- `observability-dashboard`: Streamlit UI with service health grid, health trend charts, log search with faceted filtering, and alert history timeline.
- `observability-otel-instrumentation`: Adds OpenTelemetry tracing to webhook-receiver and ai-review services. Propagates trace context into structlog. Exports traces, metrics, and log correlation data to Grafana LGTM (via OTLP).
- `observability-slos`: Defines SLOs for webhook delivery reliability, review latency, and scheduler availability. Implements multi-window burn-rate alerting.

### Modified Capabilities

- `webhook-ai-review-repo-split`: The inter-service handoff contract currently requires `X-Trace-Id` (format: `trace-{uuid.hex[:12]}`) on the dispatch call. This change adds a `traceparent` W3C header (propagated via OTel HTTPX instrumentation) alongside the existing `X-Trace-Id`. No existing behavior is removed or changed — the `X-Trace-Id` header and `trace_id` in the webhook response body remain identical. The `traceparent` header is additive when `OTEL_ENABLED=true`.
- `ai-review-deployment-state`: The webhook-to-ai-review handoff contract requires `X-Trace-Id` header and the webhook acceptance response includes `trace_id`. This change adds `traceparent` header propagation (additive, not replacing) and enriches structlog events with `trace_id` and `span_id` fields from the active OTel span. No existing health-check contract or dispatch behavior changes.

## Impact

### New Repository
- `tdt-observability/`: New Python package with Streamlit dashboard, health poller, log collector, and DuckDB storage.

### Dependencies Added
| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.58.0 | Dashboard UI |
| duckdb | 1.5.4 | Analytics engine |
| watchfiles | 1.2.0 | Log file tailing |
| pydantic | 2.13.4 | Data validation |
| opentelemetry-api | 1.43.0 | Tracing API |
| opentelemetry-sdk | 1.43.0 | SDK implementation |
| opentelemetry-instrumentation-fastapi | latest | Auto-instrument FastAPI |
| opentelemetry-instrumentation-httpx | latest | Trace outbound HTTP |

### Storage
- `~/.tdt/observability/health.duckdb`: DuckDB file for health snapshots and log events.
- All existing structlog output formats remain unchanged.

### Existing Services Modified
- `webhook-receiver/`: Optional OTel instrumentation added (behind a feature flag, off by default).
- `ai-review/`: Optional OTel instrumentation added (behind a feature flag, off by default).

### Docker (Phase 3)
- `grafana/otel-lgtm:v0.28.0` for local OTel backend (Grafana + Loki + Tempo + Mimir).
