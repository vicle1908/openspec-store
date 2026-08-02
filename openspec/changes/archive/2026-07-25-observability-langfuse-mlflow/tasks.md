## 0. OTel Gap Fix — Prerequisite (before observability integration)

- [x] 0.1 Add OTel span to `llm_gateway/gateway.py` `BifrostGateway.complete()` (line 243): wrap the HTTP call with `tracer.start_as_current_span("llm.complete")` capturing `gen_ai.system`, `gen_ai.request.model`, `gen_ai.response.usage.prompt_tokens`, `gen_ai.response.usage.completion_tokens`, `gen_ai.usage.cost_usd`, `gen_ai.response.finish_reason`. Same for `LiteLLMGateway.complete()` (line 437). Add `get_tracer("agent_core.llm_gateway")` import. Unit test: verify span created with correct attributes.
- [x] 0.2 Add OTel span to `tool_registry/registry.py` `ToolRegistry.execute()` (line 123): wrap the tool execution with `tracer.start_as_current_span("tool.execute")` capturing `agent_core.tool.name`, `agent_core.tool.args` (redacted), `agent_core.tool.output_length`, `agent_core.tool.duration_ms`, `agent_core.tool.success`. Add `get_tracer("agent_core.tool_registry")` import. Unit test: verify span created with correct attributes.
- [x] 0.3 Verify full trace tree: agent span → LLM spans (with token/cost data) → tool spans (with args/results). Run `agent-core health` with OTel Collector to confirm all spans arrive. This is a prerequisite for Langfuse integration — without these spans, Langfuse would only see the outer agent trace.

## 1. Infrastructure — Docker Compose Stack

- [x] 1.1 Add Langfuse v3 services to `compose.yaml`: `langfuse/langfuse:3.219` (Web container, port 3000), `langfuse/langfuse:3.219` (Worker container, async processing), `clickhouse/clickhouse-server:latest` (trace storage, ports 8123/9000), `postgres:16` (langfuse-postgres, separate from existing agent_core postgres), `redis:7-alpine` (langfuse-redis), `quay.io/minio/minio:latest` (shared MinIO, ports 9000/9001 — all local, no cloud). Set resource limits: ClickHouse 4GB, Web 4GB, Worker 4GB, MinIO 1GB, Redis 512MB. Verify all containers start and health check at `localhost:3000/api/public/health` returns 200.
- [x] 1.2 Add MLflow services to `compose.yaml`: `ghcr.io/mlflow/mlflow:3.14.0` (server, port 5000), `postgres:16` (mlflow-postgres, separate from agent_core and langfuse postgres). Configure MLflow command: `mlflow server --backend-store-uri postgresql://mlflow:${MLFLOW_DB_PASSWORD}@mlflow-postgres:5432/mlflow --artifacts-destination s3://mlflow --serve-artifacts --host 0.0.0.0 --port 5000`. Set env (all local MinIO): `AWS_ACCESS_KEY_ID=minio`, `AWS_SECRET_ACCESS_KEY=miniosecret`, `MLFLOW_S3_ENDPOINT_URL=http://minio:9000`, `MLFLOW_S3_IGNORE_TLS=true`. Verify MLflow UI accessible at `localhost:5000`.
- [x] 1.3 Add OTel Collector service to `compose.yaml`: `otel/opentelemetry-collector-contrib:0.157.0` with `otel-collector-config.yaml` mounted at `/etc/otelcol-contrib/config.yaml`. Configure OTLP receiver (gRPC 4317, HTTP 4318), batch processor (timeout 10s, send_batch_size 500), and OTLP exporter to Langfuse (`http://langfuse-web:4317`). Verify Collector starts and accepts OTLP connections.
- [x] 1.4 Create `.env.docker.example` with all required environment variables (all local, no cloud):
  - Langfuse core: `LANGFUSE_SECRET_KEY=<generate-256bit-hex>`, `LANGFUSE_NEXT_AUTH_SECRET=<random-secret>`, `ENCRYPTION_KEY=<generate-256bit-hex>`, `SALT=<random-salt>`
  - Langfuse DB: `DATABASE_URL=postgresql://langfuse:langfuse@langfuse-postgres:5432/langfuse`, `CLICKHOUSE_URL=http://langfuse-clickhouse:8123`, `CLICKHOUSE_MIGRATION_URL=langfuse-clickhouse:9000`, `REDIS_CONNECTION_STRING=redis://langfuse-redis:6379`
  - Langfuse S3 (MinIO): `LANGFUSE_S3_EVENT_UPLOAD_BUCKET=langfuse`, `LANGFUSE_S3_EVENT_UPLOAD_REGION=us-east-1`, `LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID=minio`, `LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY=miniosecret`, `LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT=http://minio:9000`, `LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE=true`, `LANGFUSE_S3_EVENT_UPLOAD_PREFIX=events/`
  - MLflow: `MLFLOW_DB_PASSWORD=mlflow_dev`
  - MinIO: `MINIO_ROOT_USER=minio`, `MINIO_ROOT_PASSWORD=miniosecret`
  Document in `docs/observability.md`.
- [x] 1.5 Add MinIO bucket initialization: create an init container or startup script that creates `langfuse` and `mlflow` buckets on first MinIO startup using `mc alias set local http://minio:9000 minio miniosecret && mc mb local/langfuse && mc mb local/mlflow`.
- [x] 1.6 Validate full stack: `docker compose up -d` starts all services (3 existing + ~10 new = ~13 total). Run `docker compose ps` — all containers healthy. Run `agent-core health` — reports Langfuse/MLflow/Collector status. Verify Langfuse UI at `localhost:3000`, MLflow UI at `localhost:5000`, MinIO console at `localhost:9001`.

## 2. Langfuse Integration — Client & Instrumentation

- [x] 2.1 Create `src/agent_core/observability/__init__.py` with public API: `LangfuseClient`, `MLflowClient`, `run_evaluation`. Create `src/agent_core/observability/langfuse_client.py` with `LangfuseClient` class: `create()` factory (reads config from `ObservabilitySettings`, uses `langfuse.get_client()` v4 API), no-op fallback when unconfigured, `score()` method (uses `span.score_trace()` v4 API), `get_trace_id()` context accessor.
- [x] 2.2 Add Langfuse SDK dependency to `pyproject.toml`: `langfuse>=4.14.0,<5` (v4 is current major, released March 2026). Run `uv sync` and verify import. Extend `ObservabilitySettings` in `foundation/settings.py` (currently at line 141) with new fields: `langfuse_host`, `langfuse_public_key`, `langfuse_secret_key`, `langfuse_inline_tracing`. Add `LANGFUSE_*` env prefix. Add config keys to `config.yaml.example`: `observability.langfuse_host`, `observability.langfuse_public_key`, `observability.langfuse_secret_key`.
- [x] 2.3 Update `agent_base/hooks/builtins.py` to add Langfuse integration hooks: register a new `langfuse_hooks()` hook pack function that hooks into `HookPoint.RUN` AFTER (to record trace metadata and scores) and `HookPoint.TOOL_EXECUTE` AFTER (to record tool spans). The hook pack SHALL read Langfuse config from settings and be a no-op when unconfigured. Register in `register_pack()` alongside existing hooks.
- [x] 2.4 Implement score recording in `observability/langfuse_client.py`: after agent run, record scores `success`, `accuracy`, `tool_success_rate`, `cost_usd` via `langfuse.score()`. Implement deduplication: use `_langfuse_scores_recorded` flag in context dict to prevent double-recording (since `HookPoint.RUN` AFTER hooks fire twice — once from agent.py:337, once from HookAdapter). Verify scores appear once on trace in Langfuse UI.
- [x] 2.5 Implement session grouping: pass `session_id` from `AgentRequest` to Langfuse trace via `langfuse_context.update_current_trace(session_id=...)`. Verify multi-turn traces group under same session.
- [x] 2.6 Add Langfuse health check to `cli/` health command: verify Langfuse API is reachable and returns valid response. Add to `agent-core health` output.

## 3. OTel Collector — Routing Configuration

- [x] 3.1 Create `otel-collector-config.yaml` with OTLP receiver, batch processor, and OTLP exporter to Langfuse. Include filter processor to exclude health check spans. Test: emit a test span from Python, verify it appears in Langfuse via Collector.
- [x] 3.2 Update `foundation/tracing.py`: add `otel_collector_endpoint` parameter to `configure_tracing()`. Deprecate `otel_endpoint` (keep for backward compat). Default endpoint: `http://otel-collector:4317`. Verify spans route through Collector to Langfuse.
- [x] 3.3 Update `config.yaml.example`: add `observability.otel_collector_endpoint: "http://otel-collector:4317"`. Update `observability.otel_endpoint` comment to note deprecation. Verify config loads correctly.
- [x] 3.4 Add OTel span to `llm_gateway/gateway.py` `BifrostGateway.complete()` (line 243): wrap the HTTP call with `tracer.start_as_current_span("llm.complete")` capturing model, tokens, cost, latency. Same for `LiteLLMGateway.complete()` (line 437). Verify LLM call spans appear in Langfuse as children of agent span.
- [x] 3.5 Add OTel span to `tool_registry/registry.py` `ToolRegistry.execute()` (line 123): wrap the tool execution with `tracer.start_as_current_span("tool.execute")` capturing tool name, args (redacted), output length, duration, success. Verify tool spans appear in Langfuse as children of agent span.
- [x] 3.6 Verify full trace tree in Langfuse: agent span → LLM spans (with token/cost data) → tool spans (with args/results). Confirm no missing gaps.

## 4. MLflow Integration — Client & Experiments

- [x] 4.1 Create `src/agent_core/observability/mlflow_client.py` with `MLflowClient` class: `create()` factory (reads `ObservabilitySettings.mlflow_tracking_uri`), no-op fallback, `start_run()`, `log_params()`, `log_metrics()`, `log_tags()`. Extend `ObservabilitySettings` in `foundation/settings.py` with new fields: `mlflow_tracking_uri`, `mlflow_experiment_name`. Add `MLFLOW_*` env prefix. Add MLflow dependency to `pyproject.toml`: `mlflow>=3.14.0,<4` (latest stable: 3.14.0, June 2026).
- [x] 4.2 Register MLflow integration hooks in `agent_base/hooks/builtins.py`: add `mlflow_hooks()` hook pack that hooks into `HookPoint.RUN` AFTER (to log experiment params/metrics) and `HookPoint.MODEL_REQUEST` AFTER (to log per-call metrics alongside existing cost_tracker). Conditional on MLflow configured. Register in `register_pack()`.
- [x] 4.3 Implement experiment logging: after each agent run, log params (`agent_name`, `model`, `skill`, `max_iterations`, `temperature`) and metrics (`latency_ms`, `cost_usd`, `tokens_prompt`, `tokens_completion`, `iterations`, `success`, `tool_success_rate`). Log tags (`tools_used`, `environment`). Verify in MLflow UI.
- [x] 4.4 Implement cost tracking in MLflow hook: in the `mlflow_hooks()` hook pack, accumulate cost from `HookPoint.MODEL_REQUEST` AFTER responses (reading `LLMUsage.cost_usd` from the response, same as existing `cost_tracker` at `builtins.py:217-249`) and log total to MLflow at `HookPoint.RUN` AFTER. Verify cost appears in MLflow experiment metrics.

## 5. MLflow — Prompt Registry & Optimization

- [x] 5.1 Implement `MLflowClient.register_prompt()`: register system prompts in MLflow Prompt Registry with commit messages. Implement `load_prompt()` with alias support (`:production`, `:challenger`). Test: register a prompt, load by alias, verify in MLflow UI.
- [x] 5.2 Implement `MLflowClient.optimize_prompt()`: wrap `mlflow.genai.optimize_prompts()` with GEPA engine. Log optimization runs to MLflow. Verify optimized prompt appears as new version in Prompt Registry with diff view.
- [x] 5.3 Implement `MLflowClient.register_agent_config()`: serialize agent flavor config as MLflow model artifact. Implement `promote_to_production()` for lifecycle stage transitions. Verify in MLflow Model Registry UI.

## 6. MLflow — Evaluation Framework

- [x] 6.1 Implement `MLflowClient.create_eval_dataset()`: create datasets from JSONL files. Implement `evaluate_against_dataset()` wrapping `mlflow.genai.evaluate()`. Verify evaluation results logged to MLflow with per-sample scores.
- [x] 6.2 Implement `MLflowClient.evaluate()` with built-in scorers: `Correctness`, `Safety`, `RelevanceToQuery`, `Guidelines` from `mlflow.genai.scorers`. Use `mlflow.genai.evaluate(data=dataset, predict_fn=agent.run, scorers=[...])` syntax (MLflow 3.14.0). Test against a sample agent run dataset. Verify scores in MLflow UI.

## 7. Scorer Framework

- [x] 7.1 Create `src/agent_core/observability/scorers/__init__.py` with public exports. Create `latency.py` with `LatencyScorer` (threshold-based 0-1 scoring). Create `cost.py` with `CostScorer` (cost-per-token efficiency). Create `tool_usage.py` with `ToolUsageScorer` (tool success rate). Unit tests for all scorers.
- [x] 7.2 Create `regression.py` with `RegressionScorer`: compares current run metrics against baseline window (query Langfuse/MLflow for historical data). Detects latency regression (>20% degradation) and success rate regression (>10% drop). Unit tests with mock baseline data.
- [x] 7.3 Create `correctness.py` with `CorrectnessJudge` (LLM-as-Judge). Create `relevance.py` with `RelevanceJudge`. Implement configurable model parameter (default `openai:gpt-4o`). Unit tests with mock LLM responses.
- [x] 7.4 Implement Langfuse integration for scorers: `evaluate_langfuse(trace_id, trace_data)` method on each scorer that records results via `langfuse.score()`. Test: run scorer, verify score appears on Langfuse trace.
- [x] 7.5 Implement MLflow integration for scorers: expose each scorer as `@mlflow.genai.scorer` decorated function (MLflow 3.14.0 syntax: `from mlflow.genai.scorers import scorer`). Scorers receive `inputs`, `outputs`, `expectations`, `trace` kwargs. Return `Feedback(value=..., rationale=...)` or simple value. Test: pass scorer to `mlflow.genai.evaluate(data=traces, scorers=[...])`, verify results logged.
- [x] 7.6 Create `run_evaluation()` orchestrator: accepts traces, code scorers, judge scorers, and target backends. Executes all scorers, records results to specified backends, returns summary report. Integration test with Langfuse + MLflow.

## 8. EvalMetrics Migration

- [x] 8.1 Update `evaluation/store.py` `EvalMetrics.record()`: dual-write to both Postgres (existing) and Langfuse scores + MLflow metrics. Verify both backends receive data after an agent run.
- [x] 8.2 Update `evaluation/store.py` `EvalMetrics.query()`: implement parallel query from Langfuse (ClickHouse SQL) and MLflow (search_runs). Return unified results. Verify query parity with direct Postgres query.
- [x] 8.3 Run validation period: dual-write for 2-4 weeks. Compare Langfuse/MLflow query results against Postgres. Document any discrepancies.
- [x] 8.4 After validation: create migration script to export existing `eval_metrics` data to MLflow. Drop `agent_memory.eval_metrics` table. Deprecate `evaluation/store.py` (keep for backward compat, re-export from observability). Remove `evaluation/migrations_eval.py`.

## 9. Hook Pack Updates

- [x] 9.1 Create new `langfuse_hooks()` hook pack in `agent_base/hooks/builtins.py`: hooks into `HookPoint.RUN` AFTER (record trace metadata and scores via Langfuse) and `HookPoint.TOOL_EXECUTE` AFTER (record tool span details). Register in `register_pack()` at `builtins.py:251`. Verify Langfuse scores update after agent run.
- [x] 9.2 Create new `mlflow_hooks()` hook pack in `agent_base/hooks/builtins.py`: hooks into `HookPoint.RUN` AFTER (log experiment params/metrics) and `HookPoint.MODEL_REQUEST` AFTER (accumulate cost from `LLMUsage.cost_usd`, same pattern as existing `cost_tracker` at line 217-249). Register in `register_pack()`. Verify cost and metrics appear in MLflow.
- [x] 9.3 Preserve existing `otel_metrics`, `structured_audit`, `cost_tracker`, `approval_gate` hook packs unchanged. Verify all existing hook tests pass (`tests/agent_base/test_hook_packs.py`).

## 10. CLI & Documentation

- [x] 10.1 Add `agent-core observability status` CLI command: check Langfuse, MLflow, and OTel Collector connectivity. Display service status, trace count, last activity. Add to `cli/` module.
- [x] 10.2 Add `agent-core eval run <dataset>` CLI command: run evaluation against a registered MLflow dataset with configured scorers. Display results summary. Add to `cli/` module.
- [x] 10.3 Add `agent-core eval compare <run1> <run2>` CLI command: compare two MLflow experiment runs side-by-side. Display parameter diff and metric deltas. Add to `cli/` module.
- [x] 10.4 Create `docs/observability.md`: architecture overview, Docker Compose setup guide, configuration reference, migration guide from EvalMetrics, scorer framework usage, troubleshooting. Update `docs/architecture.md` to reference observability module.
- [x] 10.5 Update `config.yaml.example` with all new observability settings. Update `README.md` with observability section. Update `AGENTS.md` with new module documentation.

## 11. Testing & Validation

- [x] 11.1 Write unit tests for `observability/langfuse_client.py`: initialization, no-op fallback, score recording, session grouping. Target: 90%+ coverage. Run `pytest tests/observability/test_langfuse_client.py -v`.
- [x] 11.2 Write unit tests for `observability/mlflow_client.py`: initialization, no-op fallback, experiment logging, prompt registry, evaluation. Target: 90%+ coverage. Run `pytest tests/observability/test_mlflow_client.py -v`.
- [x] 11.3 Write unit tests for all scorers in `observability/scorers/`: latency, cost, tool_usage, regression, correctness, relevance. Target: 90%+ coverage. Run `pytest tests/observability/scorers/ -v`.
- [x] 11.4 Write integration test: full agent run → Langfuse trace + scores → MLflow experiment + metrics. Verify both backends receive consistent data. Run `pytest tests/observability/test_integration.py -v`.
- [x] 11.5 Run full test suite: `uv run pytest tests/ -q`. Verify all existing tests pass (no regressions). Run `uv run mypy src/agent_core/ --strict`. Run `uv run ruff check src/ tests/`. Verify pre-commit hooks pass.

## 12. Cleanup & Deprecation

- [x] 12.1 Deprecate `evaluation/__init__.py`: re-export `EvalMetrics` and `EvalRecord` from `observability` module. Add deprecation warnings. Update imports in all consumers.
- [x] 12.2 Remove `evaluation/migrations_eval.py` (eval_metrics table migration). Remove `evaluation/store.py` (after migration complete). Keep `evaluation/types.py` as re-export.
- [x] 12.3 Finalize `ObservabilitySettings` in `foundation/settings.py`: ensure all Langfuse/MLflow/Collector settings are validated at startup. Update `config.yaml.example` with all new observability keys. Verify `agent-core config` shows new settings (secrets redacted).
- [x] 12.4 Final validation: full stack test with Docker Compose. Agent run → OTel span routes to Langfuse → Langfuse trace visible → MLflow experiment logged → scores recorded → evaluation runnable. All existing tests pass (`pytest tests/ -q`). Documentation complete.
