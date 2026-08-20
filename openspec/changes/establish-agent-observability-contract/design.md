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

### D10: Numeric evaluation aggregation

Pass-rate calculations SHALL use threshold comparison (`score >= threshold`), not identity comparison (`score is True`). This fixes the verified defect where numeric evaluators (e.g., `accuracy_score=0.8`) were incorrectly counted as failures.

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
span_id: str | None = Field(default=None, description="OTel root span ID when available")
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

## Open questions

1. What are the actual OTel Collector routes for Langfuse and MLflow?
2. Is `mlflow.pydantic_ai.autolog()` compatible with the installed pydantic-ai v2?
3. Does the deployed Langfuse accept OTLP Collector traces?
4. Who owns the DBOS scheduler process lifecycle for observability initialization?
5. Should sampling be configurable in this change, or deferred?
