## Why

agent-core's current observability stack is functional but fragmented: OTel traces go to a configurable endpoint (often unused), cost tracking lives in a hook, audit logs are JSONL files, and evaluation metrics sit in a custom Postgres table with hand-written SQL queries. There is no visual trace explorer, no experiment comparison UI, no prompt versioning, and no LLM-as-judge evaluation. As agent runs increase in complexity (multi-step workflows, sub-agents, tool chains), the team needs production-grade observability that shows the full picture — from LLM calls to tool execution to cost — in one place, plus experiment tracking to compare agent configurations and evaluate quality systematically.

## What Changes

- **Add Langfuse** (self-hosted, Docker Compose) as the primary observability backend: full-stack OTel traces, LLM conversation replay, cost monitoring, score-based evaluation, and dashboards.
- **Add MLflow** (self-hosted, Docker Compose) as the experiment tracking and model lifecycle backend: experiment comparison, prompt registry with versioning and A/B testing, prompt optimization (GEPA/DSPy), GenAI evaluation scorers (including Agent GPA and TruLens integration), and model registry for agent configurations.
- **Add OTel Collector** as a routing layer between agent-core and observability backends, enabling future backend additions (e.g., Logfire Cloud) without code changes.
- **Replace `evaluation/` module** (EvalMetrics class, eval_metrics Postgres table) with Langfuse scores + MLflow experiment logging. EvalRecord remains as the canonical data model.
- **Replace hook packs** (structured_audit, cost_tracker) with Langfuse trace-based audit trail and unified cost tracking.
- **Update `foundation/tracing.py`** to route OTel spans through the Collector instead of direct OTLP export.
- **Update `agent_base/agent.py`** to wrap BaseAgent.run() with Langfuse @observe() and MLflow experiment logging.
- **Add `observability/` module** with Langfuse client, MLflow client, scorer framework, and unified cost tracker.
- **Extend Docker Compose** with ~10 new containers (Langfuse 6, MLflow 3, OTel Collector 1).
- **Add CLI subcommands**: `observability status`, `eval run`, `eval compare`.

## Capabilities

### New Capabilities

- `langfuse-integration`: Langfuse SDK wrapper, @observe() instrumentation on BaseAgent, trace ingestion via OTel Collector, score recording (success, accuracy, tool_success_rate, cost), session-based multi-turn tracing, cost tracking dashboards.
- `mlflow-integration`: MLflow SDK wrapper, autolog() for Pydantic AI agents, experiment logging (params + metrics per run), prompt registry for agent system prompts, prompt optimization, GenAI evaluation with custom scorers and Agent GPA, model registry for agent configurations, evaluation datasets.
- `otel-collector-routing`: OTel Collector configuration for routing traces/metrics/logs to Langfuse (primary) with extensibility for future backends. Replaces direct OTLP export from foundation/tracing.py.
- `scorer-framework`: Reusable evaluation scorers — code evaluators (latency, cost, tool_usage, regression detection) and LLM-as-Judge evaluators (correctness, relevance, plan_adherence, execution_efficiency). Integrates with both Langfuse score system and MLflow genai.evaluate().
- `langfuse-docker-deployment`: Docker Compose stack for Langfuse v3 (ClickHouse, PostgreSQL, Redis, Web, API, Worker). Production-ready configuration with environment variable management.

### Modified Capabilities

- `foundation-tracing`: Tracing endpoint changes from direct OTLP to OTel Collector. configure_tracing() default endpoint changes. No behavioral change to span creation.
- `agent-base-hooks`: Hook packs (otel_metrics, cost_tracker, structured_audit) updated to emit to Langfuse/MLflow instead of standalone backends. Hook interface unchanged.

## Impact

- **Code**: New `observability/` module (~6 files), modified `foundation/tracing.py`, modified `agent_base/agent.py`, modified `agent_base/hooks/builtins.py`, modified `cli/`, deleted `evaluation/store.py`, deleted `evaluation/migrations_eval.py`.
- **Dependencies**: Add `langfuse>=2.0.0`, `mlflow>=3.1.0`, `opentelemetry-exporter-otlp>=1.0.0` to pyproject.toml.
- **Infrastructure**: 10 new Docker containers (Langfuse 6 + MLflow 3 + OTel Collector 1). ~8-12GB additional RAM. ClickHouse for trace storage, MinIO for MLflow artifacts.
- **Database**: New Postgres databases for Langfuse metadata and MLflow metadata (separate from existing agent_core database). Drop `agent_memory.eval_metrics` table after migration.
- **Config**: New `observability.langfuse_*`, `observability.mlflow_*`, `observability.otel_collector_endpoint` settings in config.yaml. Deprecated `observability.otel_endpoint` (direct export).
- **Backward compatibility**: EvalRecord model preserved. evaluation/ module re-exports from observability/ during transition. Existing OTel instrumentation unchanged (just re-routed).
- **Risk**: MEDIUM — new dependencies (Langfuse SDK, MLflow) are mature and well-maintained. Docker Compose stack adds operational complexity. Migration path is incremental (dual-write → validate → drop old).
