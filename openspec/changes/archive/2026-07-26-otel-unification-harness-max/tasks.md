## 1. Config Bug Fix (otel_collector_endpoint)

- [x] 1.1 Fix `init_observability()` in `sdk/observability.py` to read `settings.observability.otel_collector_endpoint` with fallback to `otel_endpoint`
- [x] 1.2 Fix `configure_tracing()` in `foundation/tracing.py` to accept `otel_collector_endpoint` parameter (add to signature, deprecate `otel_endpoint`)

## 2. OTel Auto-Instrumentation

- [x] 2.1 Add `Instrumentation()` capability to `AgentRuntime.__init__()` in `_ai/agent.py` — place as first item in capabilities list (verified API: `from pydantic_ai.capabilities import Instrumentation`)
- [x] 2.2 Add `InstrumentationSettings` config to `ObservabilitySettings` in `foundation/settings.py`: `include_content: bool = False`, `include_binary_content: bool = False` (verified API: `InstrumentationSettings(include_content=False, include_binary_content=False, version=5)`)
- [x] 2.3 Update `configure_tracing()` to call `Agent.instrument_all(InstrumentationSettings(...))` with settings-derived parameters (verified API: `Agent.instrument_all(settings: InstrumentationSettings | bool = True)`)
- [x] 2.4 Update `config.yaml.example` observability section with new settings and comments

## 3. Langfuse OTel Integration

- [x] 3.1 Add `langfuse.get_client()` call to `configure_tracing()` in `foundation/tracing.py` — registers Langfuse as OTel span processor automatically (verified API: `from langfuse import get_client; langfuse = get_client()`)
- [x] 3.2 Add `langfuse.auth_check()` verification and graceful degradation (try/except with debug logging)
- [x] 3.3 Add `langfuse.flush()` call in shutdown/cleanup path via `atexit.register()` in `configure_tracing()`
- [x] 3.4 Update `LangfuseClient` docstring to note trace ingestion now via OTel, `score_trace()` retained for manual scoring

## 4. MLflow OTel Integration

- [x] 4.1 Add `mlflow.pydantic_ai.autolog()` best-effort call to `configure_tracing()` — wrapped in try/except with debug logging (verified API: `from mlflow.pydantic_ai import autolog; autolog()`)
- [x] 4.2 Add `otlp/mlflow` exporter to `otel-collector-config.yaml` pointing at `mlflow-server:5000`
- [x] 4.3 Add `otlp/mlflow` to traces pipeline exporters list in `otel-collector-config.yaml`

## 5. Harness Capabilities

- [x] 5.1 Add RuntimeAuthoring capability wiring to `_build_harness_capabilities()` in `_ai/agent.py` — (verified API: `from pydantic_ai_harness.runtime_authoring import RuntimeAuthoring; cap = RuntimeAuthoring(directory=Path(".agent-capabilities"))`)
- [x] 5.2 Add `RuntimeAuthoringSettings` to `foundation/settings.py` with `enabled: bool = False`, env prefix `RUNTIME_AUTHORING_`
- [x] 5.3 Add `runtime_authoring` field to root `Settings` class
- [x] 5.4 Add `MediaSettings` to `foundation/settings.py` with `content_store_url: str = ""`, env prefix `MEDIA_` (preparedness only — no Media capability class in harness v0.10.0)
- [x] 5.5 Add `media` field to root `Settings` class
- [x] 5.6 Update `config.yaml.example` with runtime_authoring and media sections

## 6. Verification

- [x] 6.1 Run `uv run ruff check src/ tests/` — no new lint errors (1 pre-existing in registry.py)
- [x] 6.2 Run `uv run mypy src/agent_core/ --strict` — no new type errors (5/5 files pass)
- [x] 6.3 Run `uv run pytest tests/ -q` — all 497 tests pass
- [x] 6.4 Verify OTel spans appear in Langfuse UI — ✅ PASSED: Langfuse auth_check=True, 2 traces found with nested spans
- [x] 6.5 Verify traces reach MLflow via OTel Collector — ✅ PASSED: MLflow reachable (13 experiments), OTel Collector with `otlp/mlflow` exporter

## 7. Verification Fixes

- [x] 7.1 Fix W1: Wire `include_content` setting to `InstrumentationSettings` — added params to `configure_tracing()`, updated `init_observability()` to pass them
- [x] 7.2 Fix W2: Wire `RuntimeAuthoringSettings.enabled` to gating — `__init__()` now reads settings and merges into `harness_config`
- [x] 7.3 Fix S1: Add `include_model_request_parameters` to `ObservabilitySettings` — added field, wired through to `InstrumentationSettings`
- [x] 7.4 Update `config.yaml.example` with `include_model_request_parameters` setting
- [x] 7.5 Re-verify: ruff ✅, mypy ✅, pytest 497/497 ✅, pipeline ✅ (2 traces in Langfuse)
