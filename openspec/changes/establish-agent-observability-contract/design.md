# Design: Establish Agent Observability Contract

## Context

The agent ecosystem has substantial observability implementation across three planes (agent runtime, Go services, operations dashboards) and six existing OpenSpec specs governing individual backends. However, process activation, telemetry correlation, privacy, evaluation linkage, exporter ownership, and shutdown behavior are not governed by one enforceable contract. The highest-priority finding is that the agent-core CLI entry point has no confirmed `init_observability()` call site, while the agent-docs-sync consumer does initialize observability at both its CLI composition root and its `observability/__init__.py` module (import-time side effect). Evaluation records lack trace linkage, the MLflow client has verified defects in exception suppression and numeric score aggregation, and the actual deployment topology of the OTel Collector, Langfuse, and MLflow has not been audited.

### Corrected assumptions from research

- The store already contains six observability-related specs. There is no *unified ecosystem-wide lifecycle contract*, but individual backend contracts are extensive.
- `agent-docs-sync` does initialize observability. The activation gap is specific to the agent-core CLI path, not the entire ecosystem.
- Deployment topology (Collector routes, Langfuse ingestion mode, MLflow OTLP compatibility) remains unverified and must be validated before finalizing exporter routing.

## Goals

- Establish a single lifecycle and correlation contract that all backend-specific specs must satisfy.
- Make observability activation explicit, verifiable, and consumer-owned.
- Link evaluation records to traces without breaking existing evaluation workflows.
- Correct verified defects in the MLflow integration.
- Provide conformance test coverage for activation, correlation, privacy, and shutdown.
- Classify evidence levels honestly (no deployment-readiness claims without backend validation).

## Non-goals

- Replacing any existing backend (Langfuse, MLflow, Prometheus, Grafana).
- Building custom trace storage.
- Implementing memory, MCP, DBOS, or handoff span instrumentation.
- Cross-language propagation validation (separate follow-up).
- Selecting sampling percentages (deferred pending volume evidence).

## Decisions

### D1: Stable service identity

`service.name` SHALL be `agent-core` for agent-core processes and the consumer's registered name (e.g., `agent-docs-sync`) for consumers. Per-command or per-subcommand identity SHALL be an attribute (`agent_core.command.name`), not a resource label. This prevents high-cardinality `service.name` values.

### D2: Composition-root initialization

Every supported process entry point SHALL initialize observability exactly once at its composition root. Library modules SHALL NOT initialize global telemetry as a side effect. The agent-core CLI callback (`cli/app.py`) SHALL call `init_observability(service_name="agent-core")` before dispatching any subcommand.

### D3: No import-time global initialization

`agent-docs-sync/observability/__init__.py` currently calls `init_observability()` at import time. This SHALL be migrated to the CLI composition root. The module SHALL export `get_tracer` and `get_meter` without side effects.

### D4: Idempotent process lifecycle

`init_observability()` SHALL be process-idempotent. Repeated calls with the same configuration SHALL NOT add duplicate processors or exporters. A second call with a conflicting `service_name` SHALL warn and retain the first. The implementation SHALL use a module-level guard.

### D5: Explicit and global instrumentation coordination

`Agent.instrument_all()` is the canonical path for global pydantic-ai OTel instrumentation. An explicit `Instrumentation()` capability on an `AgentRuntime` SHALL be reserved for per-agent setting overrides (e.g., different `include_content` value). The system SHALL prevent duplicate spans from both paths operating on the same logical operation.

### D6: One ingestion route per backend

Each backend (Langfuse, MLflow) SHALL have exactly one authoritative trace-ingestion route per deployment. The route SHALL be determined at configuration time and SHALL NOT change at runtime. Direct SDK ingestion and Collector ingestion SHALL NOT be active simultaneously for the same backend. This prevents duplicate traces.

**Open question:** Whether the deployed Langfuse and MLflow support OTLP Collector ingestion. This must be validated before finalizing the default route. If direct SDK is the validated default, the Collector route remains available for future migration.

### D7: Bounded flush and shutdown

Pending OTel spans SHALL be flushed before normal process exit with a bounded timeout (default 10 seconds). Backend failure SHALL NOT block process termination. The implementation MAY use `TracerProvider.force_flush()`, `shutdown()`, `atexit`, or signal handlers. Structured log flushing is best-effort and SHALL NOT block.

### D8: Trace-log correlation

A structlog processor SHALL inject `trace_id` and `span_id` from the active OTel span context into every log entry. When no span is active, these fields SHALL be absent or empty. The processor SHALL be registered during `configure_logging()`.

### D9: Evaluation-to-trace linkage

`EvalRecord` SHALL include nullable `trace_id` and `span_id` fields. The database schema SHALL include corresponding columns. When a trace is active during evaluation, these fields SHALL be populated. This enables linking quality regressions to specific agent trajectories.

### D10: Evaluation pass/fail semantics

Pass-rate SHALL be derived from boolean assertions (`ReportCase.assertions`) and task/evaluator failures. Numeric scores (`ReportCase.scores`) SHALL be reported separately as measurements with per-evaluator mean and stddev. When no assertions exist, pass rate SHALL be reported as `null` — never defaulted to a universal threshold.

### D11: MLflow exception isolation

MLflow client operations SHALL be isolated from the caller. Exceptions from `MLflowClient` wrapper methods SHALL be caught and logged, not propagated. The `_Suppress` class MUST suppress exceptions correctly.

### D12: Privacy defaults

Content capture (prompts, completions, tool payloads) SHALL be OFF by default. When `capture_sensitive_payloads` is True, known secret patterns SHALL be redacted before export. Binary content SHALL be excluded by default. Field-level redaction is out of scope for this change (follow-up).

### D13: Conformance evidence levels

Every capability SHALL be classified: specified, implemented, unit-tested, integration-tested, runtime-validated, or deployment-validated. Deployment-readiness claims SHALL NOT be made without backend validation evidence.

## Exporter topology

### Current known routes

| Backend | Route | Evidence |
|---------|-------|----------|
| Langfuse | `langfuse.get_client()` registers OTel span processor | `tracing.py:125-141` |
| MLflow | `mlflow.pydantic_ai.autolog()` + potential Collector | `tracing.py:143-152`, `mlflow-otel-integration` spec |
| OTLP Collector | `OTLPSpanExporter` in `BatchSpanProcessor` | `tracing.py:80-96` |
| Prometheus | Go `kafka/producer.go` metrics | `producer.go:22-52` |

### Deployment validation required

- Does the OTel Collector have `otlp/langfuse` and `otlp/mlflow` exporters configured?
- Does the deployed Langfuse accept OTLP traces directly?
- Does the deployed MLflow server expose an OTLP trace endpoint?
- Is `mlflow.pydantic_ai.autolog()` compatible with the installed pydantic-ai version?

## Data model changes

### `agent_memory.eval_metrics` migration

```sql
ALTER TABLE agent_memory.eval_metrics
  ADD COLUMN trace_id TEXT DEFAULT NULL,
  ADD COLUMN span_id TEXT DEFAULT NULL;

-- Nullable columns, no backfill required
-- Existing records remain valid with NULL trace/span IDs
```

### `EvalRecord` Pydantic model

```python
trace_id: str | None = Field(default=None, description="OTel trace ID when available")
span_id: str | None = Field(default=None, description="Evaluation-report span ID when available")
```

## Failure handling

| Failure | Behavior |
|---------|----------|
| OTel endpoint unconfigured | No-op tracer, application functions normally |
| `init_observability()` called twice | Second call warns, retains first config |
| Langfuse unavailable at flush | Bounded timeout, process exits normally |
| MLflow unavailable at flush | Bounded timeout, process exits normally |
| `MLflowClient` exception | Caught and logged, caller continues |
| Import-time init attempted | Warning logged, deferred to composition root |

## Risks

| Risk | Mitigation |
|------|-----------|
| Exporter topology unverified | Phase 0 evidence capture before code changes |
| `agent-docs-sync` import-time migration breaks something | Dedicated consumer migration task with activation test |
| Database migration not backward-compatible | Nullable columns, no backfill, additive only |
| Duplicate spans if both routes active | One-route-per-backend invariant enforced in `init_observability()` |
| Flush timeout too short | Configurable timeout, generous default |

## Semantic Decision Record (2026-08-20)

This section resolves all eight contradictions identified in the MoA review before implementation approval.

### SD1: Langfuse route mode — `direct` default, `collector` deferred

`get_client()` is a singleton factory that always returns a trace-enabled `Langfuse` instance. The `Langfuse` constructor supports `tracing_enabled`, `should_export_span`, `span_exporter`, and `tracer_provider` for filtering, but these are constructor-level controls — `get_client()` does not expose them.

**Decision:** The documented current default is `direct` mode (Langfuse SDK span processor via `get_client()`). `Collector` mode is conditional on Phase 0 deployment validation proving the Collector can ingest Langfuse traces. Until then, `collector` mode SHALL NOT be implemented. `disabled` mode is supported by passing `tracing_enabled=False` to the `Langfuse` constructor.

**Risk:** `LangfuseClient.create()` currently constructs a normal trace-enabled `Langfuse` client, so calling it for "manual scoring only" may itself register another span processor — a concrete duplicate-ingestion risk in `direct` mode. The implementation MUST verify that `LangfuseClient` and the OTel-registered client share the same underlying instance, or use `should_export_span` to prevent double-ingestion.

### SD2: MLflow route mode — `autolog` default, `collector` deferred

The existing spec mandates a Collector exporter. The change introduces `autolog`, `collector`, and `disabled` modes. Those behaviors conflict unless the old unconditional requirement is removed.

**Decision:** Remove the unconditional Collector requirement from the existing MLflow spec. Replace with: "Exactly one trace-ingestion route SHALL be active." Default mode is `autolog` (SDK-based). `Collector` mode is deferred pending deployment validation of the MLflow OTLP endpoint. `Disabled` mode suppresses trace export.

### SD3: Evaluation pass/fail semantics — assertions-based, not numeric

pydantic-evals supports boolean, integer, float, string, structured mapping, and reason outputs. Numeric values belong in `ReportCase.scores`; boolean pass/fail belongs in `ReportCase.assertions`. There is no universal pass threshold for numeric scores.

**Decision:** Pass rate SHALL be derived from boolean assertions and task/evaluator failures. Numeric scores SHALL be aggregated separately as measurements. Thresholds SHALL be evaluator-specific and explicitly configured — never globally assumed. When no assertions exist, pass rate SHALL be reported as undefined/null, not defaulted to a universal threshold. The current `result.value is True` check in `runners/runner.py` is correct for boolean assertions but must not apply to numeric scores. The `_log_to_mlflow` function SHALL report: (a) assertion pass rate (boolean only), (b) case success rate (task completed without exception), and (c) numeric score summary (mean/stddev per evaluator).

### SD4: Trace linkage semantics — propagate report-level IDs to EvalRecord

`EvaluationReport` already exposes `trace_id` and `span_id`. The remaining gap is in `EvalRecord` and Postgres persistence.

**Decision:** `EvalRecord.trace_id` SHALL be populated from `EvaluationReport.trace_id` (the trace containing the evaluated execution). `EvalRecord.span_id` SHALL be populated from `EvaluationReport.span_id` (the span directly representing the evaluation run). These are report-level identifiers, not per-case or ambient-context identifiers. Multiple cases within one evaluation share one evaluation trace. When evaluations run concurrently, each gets its own trace ID from the active OTel context.

### SD5: Service identity — stable, not variable per command

**Decision:** `service.name` SHALL be `agent-core` for agent-core processes. Per-command identity SHALL be `agent_core.command.name` attribute on the root span. This prevents high-cardinality `service.name` values.

### SD6: Consumer initialization — explicit migration, not implicit contradiction

`agent-docs-sync/observability/__init__.py` currently performs initialization at import time. The plan requires no import-time side effects.

**Decision:** Add `agent-docs-sync-observability` as a modified capability. Specify: "Observability initialization SHALL occur at the process composition root and SHALL NOT occur as an import side effect." The `agent-docs-sync` CLI callback SHALL call `init_observability(service_name="agent-docs-sync")`. The `observability/__init__.py` module SHALL export `get_tracer` and `get_meter` without side effects. This migration is a prerequisite for implementation tasks 2.6.

### SD7: Privacy scope — minimum credential redaction only

**Decision:** This change commits to: (a) content capture off by default, (b) binary content off by default, (c) explicit opt-in for prompt/tool payload capture, (d) minimum credential redaction (API keys, tokens, passwords) when `capture_sensitive_payloads=True`. Generalized PII classification, tenant-specific redaction, and field-level masking are explicit follow-up scope. Precedence rule: `include_content=False` means content is never captured; `include_content=True` permits capture; redaction always runs before export; `capture_sensitive_payloads` cannot bypass mandatory secret redaction.

### SD8: Implementation gates — no code changes until decisions closed

**Decision:** No exporter-route implementation until Collector/backend evidence is captured (Phase 0). No numeric pass-rate implementation until evaluator semantics are approved (this record). No database migration until trace/span ownership is defined (this record). No removal of import-time consumer initialization until consumer startup tests exist (task 0.6).

## Open questions (deferred to Phase 0 evidence capture)

1. What are the actual OTel Collector routes for Langfuse and MLflow?
2. Is `mlflow.pydantic_ai.autolog()` compatible with the installed pydantic-ai v2?
3. Does the deployed Langfuse accept OTLP Collector traces?
4. Who owns the DBOS scheduler process lifecycle for observability initialization?
5. Should sampling be configurable in this change, or deferred?

## Phase 0 Evidence Addendum (2026-08-20)

### Collector Configuration Inventory

| Config File | Exporters | Pipelines | Status |
|-------------|-----------|-----------|--------|
| `agent-core/otel-collector-config.yaml` | `otlp/langfuse` (langfuse-web:4317), `otlp/mlflow` (mlflow-server:5000) | traces→[langfuse, mlflow], metrics→[langfuse], logs→[langfuse] | Production-like, backends unreachable locally |
| `go-microservices/deploy/otel-collector-config.yaml` | `debug` only | traces/metrics/logs→[debug] | Local-dev config, no backend exporters |

**Divergence:** The two configs are intentionally different — agent-core routes to Langfuse/MLflow for observability, go-microservices uses debug for local development. Cross-language trace correlation is NOT possible with current configs (different Collector instances, no shared backend).

### Backend Reachability

| Backend | Local Endpoint | Status | OTLP Verified |
|---------|---------------|--------|:---:|
| Langfuse | `localhost:3000` | Unreachable (no container) | No |
| MLflow | `localhost:5000` | 403 (no container or auth required) | No |

### Route Decisions

| Backend | Default Mode | Collector Mode | Rationale |
|---------|-------------|----------------|-----------|
| Langfuse | `direct` (SDK span processor via `get_client()`) | Deferred | OTLP endpoint unverified; `get_client()` confirmed working |
| MLflow | `autolog` (`mlflow.pydantic_ai.autolog()`) | Deferred | autolog() confirmed compatible with pydantic-ai v2; OTLP endpoint unverified |

### autolog Compatibility

`mlflow.pydantic_ai.autolog()` succeeds with non-fatal warning: `Error importing pydantic_ai.mcp.MCPServer: module 'pydantic_ai.mcp' has no attribute 'MCPServer'`. This does not block trace export.

## Phase 2 Composition-Root Addendum (2026-08-20)

### DBOS and worker ownership

The current topology has one DBOS scheduler worker and several consumers; the
consumer repositories do not own a second scheduler worker process.

| Process / role | Composition root | DBOS responsibility | Observability disposition |
|---|---|---|---|
| agent-core CLI | `agent-core/src/agent_core/cli/app.py:main` | The `schedules` subcommands are client/inspection calls through `tdt_core.scheduler`; they do not run a worker loop. | Initialize `init_observability(service_name="agent-core")` in the callback before subcommand dispatch. |
| Central scheduler worker | `tdt-scheduler/compose.yaml:17` launches `uv run tdt-scheduler serve`; the long-lived loop is `tdt-core/src/tdt_core/scheduler/cli.py:_serve` | Sole process allowed to call `SchedulerEngine.apply_schedules()` and own DBOS scheduled-workflow ticks. | This worker's own initialization is outside agent-core; no DBOS spans are added in this change. |
| agent-core scheduler adapter | `agent-core/src/agent_core/scheduler_setup.py:_apply_yaml_manifests` | Loads schedule manifests when explicitly imported; it is not a worker or process entry point. | No initialization side effect is added here. |
| agent-harness consumer | `agent-harness/src/agent_harness/cli.py:app` | Durable state is LangGraph/Postgres; optional DBOS scheduling may trigger the runner but does not replace its checkpoint root. | Consumer lifecycle remains separately scoped; no DBOS spans are added here. |
| code-daily-scan consumer | `code-daily-scan/src/code_daily_scan/dbos_scheduling.py:register_all_schedules` | Registers manifest schedules for the central scheduler; it does not own the worker loop. | No DBOS spans are added here. |

The central `tdt-scheduler` process is therefore the DBOS worker composition
root. The agent-core CLI composition root is the only root changed in this
phase; adding scheduler-worker observability initialization or DBOS spans is a
separate follow-up concern.

## Closure Evidence Addendum (2026-08-21)

### Integrated implementation commits

| Repository | Commit | Scope |
|---|---|---|
| `agent-core` | `f1642f9` | Global/explicit Pydantic AI instrumentation ownership and behavioral span-tree matrix |
| `agent-core` | `4107df8` | Typed backend route modes, deferred Collector handling, route/settings tests |
| `agent-core` | `3b9583f` | Neutral debug-only Collector topology and singleton-safe Langfuse scoring client |
| `agent-core` | `1c8cf12` | Command identity, bounded lifecycle shutdown, evaluation recording seam, scheduler wrapper, OTLP gRPC dependency and subprocess probe |
| `agent-core` | `25e3280` | Checkout-stable lint evidence annotations for editable `tdt-core` classification |
| `agent-docs-sync` | `c6c5b1f` | Side-effect-free observability module and startup-order activation tests |
| `tdt-scheduler` | `4a73580` | Container entrypoint/Compose delegation to `agent-core-scheduler` composition root |

### Current evidence levels

- Specified: OpenSpec validation passes for the selected change and full store.
- Implemented: integrated source commits above are present in the default repositories.
- Unit-tested: full agent-core pytest passes with only declared environment-dependent skips; docs-sync focused lifecycle tests pass.
- Integration-tested: local OTLP gRPC receiver accepted a real `agent-core health` subprocess span before exit.
- Runtime-validated: the local transport, bounded exit flush, command identity, and scheduler composition ordering are validated.
- Deployment-validated: not claimed. Langfuse and MLflow endpoints were not reachable locally; real backend UI/OTLP acceptance remains outstanding.

### Remaining follow-up scope

`agent-harness` and `code-daily-scan` still do not own observability initialization and remain follow-up consumer changes. Cross-language propagation, memory/MCP/DBOS/handoff span instrumentation, sampling policy, and real Langfuse/MLflow deployment acceptance remain outside this change.
