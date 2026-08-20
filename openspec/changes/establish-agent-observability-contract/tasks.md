# Tasks

## 0. Reconcile evidence and deployment topology

- [ ] 0.1 Correct the baseline report at `openspec-store/openspec/reports/agent-ecosystem-observability-research.md`: (a) existing observability specs exist (`otel-auto-instrumentation`, `langfuse-otel-integration`, `mlflow-otel-integration`, `observability-tests`, `evaluation`, `agent-docs-sync-observability`); (b) agent-docs-sync initializes observability; (c) agent-core CLI activation is the confirmed gap; (d) Graphify/GitNexus were loaded but not queried — remove claims of graph-based evidence. **Evidence:** corrected file committed.
- [ ] 0.2 Inventory actual OTel Collector configuration and deployed routes. **Repo:** go-microservices. **Validation:** `cat deploy/otel-collector-config.yaml` and report exporters. **Evidence:** artifact path.
- [ ] 0.3 Verify whether deployed Langfuse accepts Collector OTLP ingestion. **Validation:** curl Langfuse `/api/otel/v1/traces` or check Langfuse deployment docs. **Evidence:** captured response or documented blocker.
- [ ] 0.4 Verify whether deployed MLflow accepts OTLP traces. **Validation:** curl MLflow `/api/2.0/mlflow/traces/search-otel` or check version. **Evidence:** captured response or documented blocker.
- [ ] 0.5 Verify compatibility of `mlflow.pydantic_ai.autolog()` with installed pydantic-ai v2. **Repo:** agent-core. **Validation:** `uv run python -c "from mlflow.pydantic_ai import autolog; autolog()"` exits 0. **Evidence:** captured output.
- [ ] 0.6 Record selected authoritative route for each backend (direct SDK or Collector) based on evidence. **Evidence:** route decision documented in design.md addendum.
- [ ] 0.7 Reconcile Langfuse and MLflow delta specs with route evidence before implementation. If deployment validation proves Collector is not available, modify deltas to retain direct SDK as default.
- [ ] 0.8 Disposition consumer repos `agent-harness` and `code-daily-scan`: inspect entry points, determine whether each requires composition-root initialization. **Repo:** agent-harness, code-daily-scan. **Validation:** document whether each has standalone CLI/worker processes that need `init_observability()`. **Evidence:** consumer inventory updated in design.md.

## 1. Lock regression tests for confirmed defects

- [ ] 1.1 Add a failing test proving `MLflowClient` exceptions currently propagate. **Repo:** agent-core. **File:** `tests/observability/test_mlflow_client.py`. **Validation:** test fails before fix. **Evidence:** pytest output.
- [ ] 1.2 Add a failing test proving current MLflow evaluation summary mishandles the distinction among assertions, numeric scores, and task failures. **Repo:** agent-core. **File:** `tests/observability/scorers/test_runner.py`. **Validation:** test fails before fix. **Evidence:** pytest output.
- [ ] 1.3 Add a failing test proving agent-core CLI does not currently initialize tracing. **Repo:** agent-core. **File:** `tests/cli/test_cli_tracing_init.py`. **Validation:** test fails before fix. **Evidence:** pytest output.
- [ ] 1.4 Add a test for repeated observability initialization (idempotency). **Repo:** agent-core. **File:** `tests/foundation/test_tracing_extended.py`. **Validation:** test passes with no-op provider, fails if duplicate processors. **Evidence:** pytest output.
- [ ] 1.5 Run focused test suite and preserve pre-fix evidence. **Repo:** agent-core. **Validation:** `uv run pytest tests/observability/ tests/cli/ tests/foundation/test_tracing*.py -v`. **Evidence:** full pytest output.

## 2. Implement lifecycle initialization

- [ ] 2.1 Run GitNexus `impact` for every symbol to be modified (`init_observability`, `configure_tracing`, `configure_logging`, `cli/app.py`, `sdk/observability.py`). **Repo:** agent-core. **Evidence:** impact report captured.
- [ ] 2.2 Make `init_observability()` process-idempotent with a module-level guard. **Repo:** agent-core. **File:** `src/agent_core/sdk/observability.py`. **Validation:** second call with same config produces no duplicate processors. **Evidence:** test 1.4 passes.
- [ ] 2.3 Configure OTel metrics (`configure_metrics()`) from the same `init_observability()` call when an endpoint is set. **Repo:** agent-core. **File:** `src/agent_core/sdk/observability.py`. **Validation:** `get_meter()` returns non-no-op meter after initialization. **Evidence:** pytest output.
- [ ] 2.4 Wire agent-core CLI with `init_observability(service_name="agent-core")` at its composition root (`cli/app.py` callback). **Repo:** agent-core. **File:** `src/agent_core/cli/app.py`. **Validation:** CLI command emits OTel span when endpoint is configured. **Evidence:** test 1.3 passes.
- [ ] 2.5 Record command identity as `agent_core.command.name` attribute on root span, not as `service.name`. **Repo:** agent-core. **File:** `src/agent_core/cli/app.py` or `src/agent_core/foundation/tracing.py`. **Validation:** exported span carries `agent_core.command.name`. **Evidence:** test assertion.
- [ ] 2.6 Remove import-time `init_observability()` call from agent-docs-sync. **Repo:** agent-docs-sync. **File:** `src/agent_docs_sync/observability/__init__.py`. **Validation:** importing `agent_docs_sync.observability` does not configure a tracer provider. **Evidence:** pytest output.
- [ ] 2.7 Identify DBOS/worker composition roots without adding DBOS spans. **Repo:** agent-core. **Validation:** document composition root paths in design.md. **Evidence:** design.md addendum.

## 3. Resolve instrumentation duplication

- [ ] 3.1 Capture the span tree with only `Agent.instrument_all()` active (no explicit `Instrumentation()`). **Repo:** agent-core. **Evidence:** span dump showing one root, one model, one tool span.
- [ ] 3.2 Capture the span tree with explicit `Instrumentation()` on AgentRuntime only. **Repo:** agent-core. **Evidence:** span dump.
- [ ] 3.3 Capture the span tree with both global and explicit instrumentation. **Repo:** agent-core. **Evidence:** span dump showing no duplicate spans.
- [ ] 3.4 Implement the selected ownership model (global canonical, explicit for overrides). **Repo:** agent-core. **File:** `src/agent_core/_ai/agent.py`. **Validation:** one span per logical operation regardless of configuration. **Evidence:** test `test_no_duplicate_spans` passes.
- [ ] 3.5 Assert one root/model/tool span per logical operation in all configurations. **Repo:** agent-core. **File:** `tests/foundation/test_tracing_extended.py`. **Evidence:** pytest output.

## 4. Correct MLflow and evaluation behavior

- [ ] 4.1 Fix MLflow exception isolation: replace `_Suppress.__exit__` returning `None` with correct behavior. **Repo:** agent-core. **File:** `src/agent_core/observability/mlflow_client.py`. **Validation:** test 1.1 passes after fix. **Evidence:** pytest output.
- [ ] 4.2 Change `_log_to_mlflow()` reporting semantics: (a) assertion pass rate from `ReportCase.assertions`, (b) task success rate from completed versus failed cases, (c) numeric score summaries separately, (d) `pass_rate=null` when no boolean assertions exist. **Repo:** agent-core. **File:** `src/agent_core/observability/scorers/runner.py`. **Validation:** test 1.2 passes after fix. **Evidence:** pytest output.
- [ ] 4.3 Add nullable `trace_id` and `span_id` fields to `EvalRecord`. **Repo:** agent-core. **File:** `src/agent_core/evaluation/types.py`. **Validation:** model accepts None and string values. **Evidence:** pytest output.
- [ ] 4.4 Add additive SQL migration: `ALTER TABLE agent_memory.eval_metrics ADD COLUMN trace_id TEXT DEFAULT NULL, span_id TEXT DEFAULT NULL`. **Repo:** agent-core. **File:** migration file. **Validation:** migration runs cleanly, existing rows unaffected. **Evidence:** migration output.
- [ ] 4.5 Populate `EvalRecord.trace_id` and `span_id` from `EvaluationReport.trace_id` and `EvaluationReport.span_id` in the evaluation recording path. **Repo:** agent-core. **File:** `src/agent_core/evaluation/store.py`. **Validation:** `EvalRecord` inserted with trace_id and span_id when EvaluationReport contains them. **Evidence:** pytest output.
- [ ] 4.6 Add tests: migration backward-compat, round-trip write/read, null-context insert, active-context insert. **Repo:** agent-core. **File:** `tests/evaluation/test_store.py`. **Evidence:** pytest output.

## 5. Add trace-log correlation and privacy controls

- [ ] 5.1 Add a structlog processor that injects `trace_id` and `span_id` from active OTel span context. **Repo:** agent-core. **File:** `src/agent_core/foundation/logging.py`. **Validation:** JSON log output contains `trace_id` inside active span. **Evidence:** pytest output.
- [ ] 5.2 Test logging inside active span (trace_id present) and outside (absent). **Repo:** agent-core. **File:** `tests/foundation/test_logging_trace_correlation.py`. **Evidence:** pytest output.
- [ ] 5.3 Preserve content-off defaults: verify `include_content=False` is the default. **Repo:** agent-core. **Validation:** test asserts default settings. **Evidence:** pytest output.
- [ ] 5.4 Add minimum secret redaction for API keys, tokens, and passwords when `capture_sensitive_payloads=true`. **Repo:** agent-core. **File:** `src/agent_core/foundation/tracing.py` or dedicated redaction module. **Validation:** redacted span attributes do not contain raw secrets. **Evidence:** pytest output.
- [ ] 5.5 Add tests proving content is absent by default and secrets are redacted when enabled. **Repo:** agent-core. **File:** `tests/foundation/test_tracing_privacy.py`. **Evidence:** pytest output.

## 6. Enforce backend route ownership

- [ ] 6.1 Implement explicit Langfuse route mode configuration based on Phase 0 evidence. **Repo:** agent-core. **File:** `src/agent_core/foundation/settings.py` and `src/agent_core/foundation/tracing.py`. **Validation:** exactly one ingestion path active per configuration. **Evidence:** test output.
- [ ] 6.2 Preserve manual Langfuse scoring independently of trace ingestion mode. **Repo:** agent-core. **Validation:** `LangfuseClient.score_trace()` works in all modes. **Evidence:** pytest output.
- [ ] 6.3 Implement explicit MLflow route mode configuration based on Phase 0 evidence. **Repo:** agent-core. **File:** `src/agent_core/foundation/settings.py` and `src/agent_core/foundation/tracing.py`. **Validation:** exactly one ingestion path active. **Evidence:** test output.
- [ ] 6.4 Reject or warn on conflicting backend routes. **Repo:** agent-core. **Validation:** startup warning when both direct and collector routes are configured for same backend. **Evidence:** test output.
- [ ] 6.5 Test backend failure isolation: unavailable Langfuse does not block MLflow or OTel export. **Repo:** agent-core. **File:** `tests/observability/test_backend_isolation.py`. **Evidence:** pytest output.

## 7. Runtime and deployment validation

- [ ] 7.1 Validate a short-lived agent-core CLI trace reaches the selected backend. **Repo:** agent-core. **Validation:** run `agent-core health` with OTLP endpoint, confirm span arrives. **Evidence:** Langfuse/MLflow UI screenshot or collector trace dump.
- [ ] 7.2 Validate expected agent/model/tool span hierarchy. **Repo:** agent-core. **Validation:** trace dump shows root `invoke_agent` → child `chat` → child `execute_tool`. **Evidence:** trace dump.
- [ ] 7.3 Validate spans flush before CLI exit. **Repo:** agent-core. **Validation:** run short CLI command, confirm all spans received by collector. **Evidence:** collector trace count matches expected.
- [ ] 7.4 Validate trace IDs correlate with structlog records. **Repo:** agent-core. **Validation:** cross-reference span trace_id with log output. **Evidence:** log output showing matching trace_id.
- [ ] 7.5 Validate evaluation records link to traces. **Repo:** agent-core. **Validation:** run evaluation inside active span, query `eval_metrics` for trace_id. **Evidence:** SQL query result.
- [ ] 7.6 Validate unavailable backends do not crash or block shutdown. **Repo:** agent-core. **Validation:** set Langfuse to unreachable host, run CLI, confirm exit 0 within timeout. **Evidence:** process output and exit code.
- [ ] 7.7 Record evidence level for each capability in design.md. **Repo:** openspec-store. **Evidence:** design.md updated.

## 8. Quality gates and closure

- [ ] 8.1 Run repository-specific tests, Ruff, mypy strict, and OpenSpec validation. **Repos:** agent-core, agent-docs-sync. **Validation:** `uv run ruff check src/ tests/ && uv run mypy src/ --strict && uv run pytest tests/ -q`. **Evidence:** clean output.
- [ ] 8.2 Run GitNexus `detect_changes()` before commits. **Repo:** agent-core. **Evidence:** detect_changes output.
- [ ] 8.3 Run `openspec validate establish-agent-observability-contract --strict --store openspec-store`. **Evidence:** exit 0.
- [ ] 8.4 Inspect `openspec show establish-agent-observability-contract --json --deltas-only --store openspec-store` to confirm only `agent-observability-contract` is ADDED and existing capabilities are MODIFIED (or ADDED with genuinely new requirement names). **Evidence:** parsed delta output.
- [ ] 8.5 Update the research report and SPEC_INDEX mappings. **Repo:** openspec-store. **Evidence:** committed changes.
- [ ] 8.6 Track MCP, memory, DBOS spans, handoffs, sampling, and cross-language propagation as separately scoped follow-up changes. **Evidence:** follow-up change names documented.
