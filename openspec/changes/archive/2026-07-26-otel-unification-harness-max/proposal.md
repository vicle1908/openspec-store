## Why

agent-core already depends on pydantic-ai, pydantic-ai-harness, Langfuse, MLflow, and OpenTelemetry — but the integrations are shallow. The Langfuse and MLflow clients are thin no-op wrappers that do manual SDK calls, missing the native OTel auto-instrumentation that pydantic-ai v2 provides out of the box. Meanwhile, 6 stable pydantic-ai-harness capabilities (Media, RuntimeAuthoring, Memory-native, Skills-harness, Macroscope, ManagedPrompt) remain unwired. Additionally, a config bug means the OTel Collector endpoint is declared in `config.yaml.example` but the code reads the deprecated empty `otel_endpoint` field, so traces never reach the collector.

This change wires the full OTel pipeline through pydantic-ai's built-in `Instrumentation` capability, adds the remaining harness capabilities, and fixes the config disconnect — unlocking Langfuse agent graph views, MLflow experiment lineage, prompt management, and binary content offloading with minimal new code.

## What Changes

- **Add `Instrumentation()` capability** to `AgentRuntime.__init__()` so all agent runs, model requests, and tool executions emit OTel spans automatically (pydantic-ai v2 API: `capabilities=[Instrumentation()]`)
- **Register Langfuse OTel span processor** via `langfuse.get_client()` in `configure_tracing()` — replaces the manual `LangfuseClient` wrapper for trace ingestion
- **Enable MLflow pydantic-ai autolog** via `mlflow.pydantic_ai.autolog()` in `configure_tracing()` — captures traces to MLflow experiment tracking
- **Add MLflow OTLP exporter** to `otel-collector-config.yaml` — dual export: traces go to both Langfuse and MLflow via the collector
- **Fix config disconnect** — `init_observability()` and `configure_tracing()` read `otel_collector_endpoint` instead of the deprecated empty `otel_endpoint`
- **Wire RuntimeAuthoring capability** in `_build_harness_capabilities()` — agents can author, validate, and load capabilities at runtime
- **Add MediaSettings** for future Media capability (harness v0.10.0 has utility module only, no drop-in capability class)
- **Add `InstrumentationSettings` config** — privacy controls (`include_content`, `include_binary_content`) configurable via settings
- **Add `MediaSettings` and `RuntimeAuthoringSettings`** to `foundation/settings.py` and `config.yaml.example`
- **Deprecate manual `LangfuseClient`** — keep `score_trace()` for manual scoring, but trace ingestion moves to OTel pipeline

## Capabilities

### New Capabilities
- `otel-auto-instrumentation`: pydantic-ai Instrumentation capability wired into AgentRuntime, creating automatic OTel spans for agent runs, model requests, and tool executions
- `langfuse-otel-integration`: Langfuse v4 `get_client()` registered as OTel span processor, enabling agent graph views and prompt management
- `mlflow-otel-integration`: MLflow pydantic-ai autolog + OTLP exporter via OTel Collector, enabling experiment lineage and 70+ built-in judges
- `harness-media-store`: pydantic-ai-harness media utilities (DiskMediaStore, S3MediaStore, externalize_media) for future Media capability — NOT a drop-in capability in v0.10.0
- `harness-runtime-authoring`: pydantic-ai-harness RuntimeAuthoring capability (AbstractCapability subclass) for dynamic capability loading at runtime

### Modified Capabilities
- `observability`: Requirements change to include OTel auto-instrumentation as primary tracing mechanism (currently manual spans only)
- `harness-integration`: Requirements change to include Media and RuntimeAuthoring in the capability matrix

## Impact

- **Files modified (7)**: `_ai/agent.py`, `foundation/tracing.py`, `foundation/settings.py`, `sdk/observability.py`, `otel-collector-config.yaml`, `config.yaml.example`, `observability/langfuse_client.py`
- **GitNexus blast radius**: LOW — `AgentRuntime` (3 upstream imports), `configure_tracing` (0 upstream), `_build_harness_capabilities` (1 upstream: `AgentRuntime.__init__`)
- **Dependencies**: Zero new — all libraries already in `pyproject.toml`
- **Breaking changes**: None — all additions are opt-in via config; existing `harness_config` dict pattern preserved
- **Docker Compose**: `otel-collector-config.yaml` updated to add MLflow exporter; no new containers needed (MLflow already in stack)
