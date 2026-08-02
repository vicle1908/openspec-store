## Context

agent-core's observability stack has three layers that currently operate independently:

1. **Manual OTel spans** in `foundation/tracing.py` — app-level spans (agent run, correlation IDs)
2. **LangfuseClient wrapper** in `observability/langfuse_client.py` — manual `start_as_current_observation()` calls via hooks
3. **MLflowClient wrapper** in `observability/mlflow_client.py` — manual `start_run()`/`log_params()`/`end_run()` calls via hooks

None of these capture the **model request** or **tool execution** spans that pydantic-ai v2's `Instrumentation` capability creates automatically. The OTel Collector exists in Docker Compose but receives no traces because `init_observability()` reads the deprecated empty `otel_endpoint` field instead of `otel_collector_endpoint`.

Meanwhile, pydantic-ai-harness provides 20 capabilities; agent-core wires 14. The remaining 6 stable capabilities (Media, RuntimeAuthoring, Memory-native, Skills-harness, Macroscope, ManagedPrompt) are available but unwired.

## Goals / Non-Goals

**Goals:**
- Every agent run, model request, and tool execution emits OTel spans via pydantic-ai's `Instrumentation` capability
- Spans flow to Langfuse (agent graphs, prompt management, evaluation datasets) AND MLflow (experiment lineage, 70+ judges) via the OTel Collector
- Fix the `otel_collector_endpoint` config disconnect so the existing Docker Compose OTel pipeline actually works
- Wire Media and RuntimeAuthoring harness capabilities
- Preserve backward compatibility — all changes are opt-in via config

**Non-Goals:**
- Replacing the custom `memory/` module with harness Memory (significant architectural decision, separate change)
- Wiring harness Skills (conflicts with existing `skill_system/`, needs separate evaluation)
- Wiring ManagedPrompt (requires Logfire dependency, separate decision)
- Wiring Macroscope/CodeReview (requires Macroscope binary, separate decision)
- Wiring SecretMasking (still in draft PR #172, not yet merged)
- Modifying the existing hook-based Langfuse/MLflow scoring (keep for manual scoring)

## Decisions

### D1: Use `Instrumentation()` capability on AgentRuntime, not `Agent.instrument_all()`

**Decision:** Add `Instrumentation()` to the capabilities list in `AgentRuntime.__init__()`.

**Rationale:** `Agent.instrument_all()` sets global defaults for agents that don't have their own `Instrumentation` capability. Since `AgentRuntime` already builds a capabilities list, adding `Instrumentation()` directly is more explicit, composable, and allows per-agent `InstrumentationSettings` (e.g., privacy controls). It also composes cleanly with the existing `ApprovalGate`, harness capabilities, and `MemoryCapability`.

**Alternatives considered:**
- `Agent.instrument_all()` — rejected because it's implicit and doesn't allow per-agent settings
- Custom `Instrumentation` subclass — unnecessary; the built-in class covers all needs

### D2: Use Langfuse `get_client()` + `LangfuseSpanProcessor` instead of manual SDK

**Decision:** Call `langfuse.get_client()` in `configure_tracing()` to register as an OTel span processor. Keep the existing `LangfuseClient.score_trace()` for manual scoring only.

**Rationale:** Langfuse v4's `get_client()` registers a `LangfuseSpanProcessor` on the global `TracerProvider`. This processor automatically captures all `gen_ai.*` spans from pydantic-ai's `Instrumentation` capability. It supports span filtering, session tracking, and agent graph visualization — none of which the manual wrapper provides.

**Alternatives considered:**
- Keep manual SDK wrapper — rejected; misses agent graphs, prompt management, evaluation datasets
- Use `@observe()` decorator — rejected; requires wrapping every function manually

### D3: Use OTel Collector as the routing hub, not direct SDK connections

**Decision:** Route traces through the OTel Collector to both Langfuse and MLflow. Add `otlp/mlflow` exporter to `otel-collector-config.yaml`.

**Rationale:** The OTel Collector already exists in Docker Compose. Adding a second exporter is a config-only change. This preserves the single-responsibility pattern: the app emits OTel spans, the collector routes them. It also avoids coupling the app to multiple observability SDKs.

**Alternatives considered:**
- MLflow dual export (`MLFLOW_TRACE_ENABLE_OTLP_DUAL_EXPORT`) — rejected; adds MLflow SDK coupling and the autolog compatibility range doesn't cover pydantic-ai v2
- Direct Langfuse SDK + direct MLflow SDK — rejected; duplicates tracing logic

### D4: Wire RuntimeAuthoring only; defer Media to future change

**Decision:** Wire RuntimeAuthoring (dynamic capability loading) as the highest-value harness addition. Defer Media to a future change.

**Rationale:** RuntimeAuthoring is a full `AbstractCapability` subclass with verified API: `RuntimeAuthoring(directory=Path(...), guidance=...)`. Media, however, does NOT have a capability class in harness v0.10.0 — `pydantic_ai_harness.media` is a utility module with `DiskMediaStore`, `S3MediaStore`, `externalize_media`, etc. Building a custom Media capability from these utilities is a separate, more complex effort. Adding `MediaSettings` now prepares for that future work. The other 4 (Memory, Skills, Macroscope, ManagedPrompt) have conflicts or dependencies that warrant separate evaluation.

### D5: Fix `otel_collector_endpoint` config disconnect

**Decision:** Update `init_observability()` and `configure_tracing()` to read `otel_collector_endpoint` (falling back to deprecated `otel_endpoint`).

**Rationale:** The config already has `otel_collector_endpoint: "http://otel-collector:4317"` but the code reads the deprecated empty field. This is a bug fix, not a design decision.

## Risks / Trade-offs

- **[Risk] `mlflow.pydantic_ai.autolog()` compatibility** → MLflow autolog's documented compatibility range is `0.1.9 <= pydantic-ai <= 1.79.0`. Pydantic AI 2.x support is pending (issue #24560). **Mitigation:** The OTel Collector → MLflow OTLP export path works independently of autolog. If autolog fails, traces still reach MLflow via the collector. Autolog is best-effort.

- **[Risk] Langfuse double-counting** → If both `get_client()` (which auto-registers as OTel processor) AND the OTel Collector's `otlp/langfuse` exporter are active, traces may reach Langfuse twice. **Mitigation:** `get_client()` applies a default filter (only `gen_ai.*` spans and known LLM instrumentation scopes). The OTel Collector export sends all spans. Langfuse deduplicates by trace ID. If this causes issues, remove the `otlp/langfuse` exporter from the collector config and rely solely on `get_client()`. Verified: `Langfuse(should_export_span=...)` accepts a custom filter callable.

- **[Risk] Privacy — span content capture** → By default, `InstrumentationSettings(include_content=True)` records prompts and completions in spans. **Mitigation:** Add `include_content` and `include_binary_content` to `ObservabilitySettings` with secure defaults (`include_content=False` for production).

- **[Risk] Harness capability import paths may differ** → `pydantic_ai_harness.media` and `pydantic_ai_harness.runtime_authoring` import paths are inferred from documentation; exact paths may vary by version. **Mitigation:** Wrap imports in `try/except ImportError` with logging, consistent with existing harness capability wiring pattern.

## Migration Plan

1. Fix `otel_collector_endpoint` config disconnect (zero-risk bug fix)
2. Add `Instrumentation()` capability to `AgentRuntime` — traces start flowing immediately
3. Register Langfuse OTel processor in `configure_tracing()` — agent graphs become visible
4. Add MLflow exporter to OTel Collector config — traces reach MLflow
5. Wire Media and RuntimeAuthoring capabilities
6. Add settings and config.yaml sections for new capabilities

**Rollback:** Remove `Instrumentation()` from capabilities list, revert OTel Collector config. All changes are additive.
