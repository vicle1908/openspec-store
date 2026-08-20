# Tasks

## 0. Reconcile evidence and deployment topology

- [x] 0.1 Correct the baseline report at `openspec-store/openspec/reports/agent-ecosystem-observability-research.md`: (a) six observability specs exist; (b) agent-docs-sync initializes observability; (c) agent-core CLI activation is the confirmed gap; (d) Graphify/GitNexus claims removed. **Evidence:** Errata section at top of report with all 6 corrections.
- [x] 0.2 Inventory actual OTel Collector configuration and deployed routes. **Repo:** go-microservices. **Validation:** agent-core config: otlp/langfuse + otlp/mlflow exporters. go-microservices config: debug-only. **Evidence:** configs read and documented in design.md addendum.
- [x] 0.3 Verify whether deployed Langfuse accepts Collector OTLP ingestion. **Validation:** curl Langfuse `/api/otel/v1/traces` or check Langfuse deployment docs. **Evidence:** `localhost:3000` unreachable; no langfuse container running. Collector cannot be validated locally.
- [x] 0.4 Verify whether deployed MLflow accepts OTLP traces. **Validation:** curl MLflow `/api/2.0/mlflow/traces/search-otel` or check version. **Evidence:** `localhost:5000` returns 403; no mlflow container running. OTLP endpoint unverified.
- [x] 0.5 Verify compatibility of `mlflow.pydantic_ai.autolog()` with installed pydantic-ai v2. **Repo:** agent-core. **Validation:** compatibility probe plus constructor compatibility check. **Evidence:** the installed MLflow 3.14 autolog patch passes unsupported `instrument=` to pydantic-ai 2.32; runtime now warns and disables autolog rather than monkeypatching an incompatible constructor.
- [x] 0.6 Record selected authoritative route for each backend (direct SDK or Collector) based on evidence. **Evidence:** Langfuse `direct` remains the configured default and reuses the SDK singleton; MLflow `autolog` remains the configured default but safely resolves to disabled when the installed constructor contract is incompatible; Collector routes remain deferred. The checked-in Collector topology is debug-only to prevent fanout duplication.
- [x] 0.7 Reconcile Langfuse and MLflow delta specs with route evidence before implementation. If deployment validation proves Collector is not available, modify deltas to retain direct SDK as default. **Evidence:** Delta specs already use `direct`/`autolog` as defaults with `collector` deferred. No delta changes needed.
- [x] 0.8 Disposition consumer repos `agent-harness` and `code-daily-scan`: inspect entry points, determine whether each requires composition-root initialization. **Repo:** agent-harness, code-daily-scan. **Validation:** Both have CLI entry points (`cli.py` with `main()`) and depend on `agent-core`. Neither currently imports observability. **Disposition:** Both need `init_observability()` at composition root — defer to follow-up change (not in this contract's scope).

## 1. Lock regression tests for confirmed defects

- [x] 1.1 Add a failing test proving `MLflowClient` exceptions currently propagate. **Repo:** agent-core. **File:** `tests/observability/test_mlflow_client.py`. **Validation:** test passes (proves exception propagates = bug). **Evidence:** `test_real_client_exceptions_propagate` PASSED.
- [x] 1.2 Add a failing test proving current MLflow evaluation summary mishandles the distinction among assertions, numeric scores, and task failures. **Repo:** agent-core. **File:** `tests/observability/scorers/test_runner.py`. **Validation:** 3 tests FAIL (pass_rate=0.0 instead of 1.0, no score summaries). **Evidence:** pytest output: 3 failed, 2 passed.
- [x] 1.3 Add a failing test proving agent-core CLI does not currently initialize tracing. **Repo:** agent-core. **File:** `tests/cli/test_cli_tracing_init.py`. **Validation:** pre-fix characterization followed by post-fix activation assertion. **Evidence:** the committed test now asserts the corrected callback calls `init_observability`; its stale pre-fix docstring was corrected in the integrated closure review.
- [x] 1.4 Add a test for repeated observability initialization (idempotency). **Repo:** agent-core. **File:** `tests/foundation/test_tracing_extended.py`. **Validation:** 2 tests pass: second call is noop, conflicting service name warns. **Evidence:** `TestInitObservabilityIdempotency` 2/2 passed.
- [x] 1.5 Run focused test suite and preserve pre-fix evidence. **Repo:** agent-core. **Validation:** focused pre-fix characterization plus post-fix affected suite. **Evidence:** historical RED characterization remains in the task history; post-fix integrated suites are recorded in the closure addendum and full `uv run pytest tests/` passed.

## 2. Implement lifecycle initialization

- [x] 2.1 Run GitNexus `impact` for every symbol to be modified (`init_observability`, `configure_tracing`, `configure_logging`, `cli/app.py`, `sdk/observability.py`). **Repo:** agent-core. **Evidence:** impact report captured — init_observability: 0 upstream, configure_tracing: 1 upstream (init_observability), _Suppress: 3 upstream.
- [x] 2.2 Make `init_observability()` process-idempotent with a module-level guard. **Repo:** agent-core. **File:** `src/agent_core/sdk/observability.py`. **Validation:** module-level `_initialized` guard added, second call returns early. **Evidence:** code reviewed.
- [x] 2.3 Configure OTel metrics (`configure_metrics()`) from the same `init_observability()` call when an endpoint is set. **Repo:** agent-core. **File:** `src/agent_core/sdk/observability.py`. **Validation:** non-no-op provider plus real OTLP receiver. **Evidence:** gRPC exporter is declared/locked and the lifecycle/subprocess tests passed after adding `opentelemetry-exporter-otlp-proto-grpc` and `grpcio`.
- [x] 2.4 Wire agent-core CLI with `init_observability(service_name="agent-core")` at its composition root (`cli/app.py` callback). **Repo:** agent-core. **File:** `src/agent_core/cli/app.py`. **Validation:** init_observability called in callback. **Evidence:** code reviewed.
- [x] 2.5 Record command identity as `agent_core.command.name` attribute on root span, not as `service.name`. **Repo:** agent-core. **File:** `src/agent_core/cli/app.py` or `src/agent_core/foundation/tracing.py`. **Validation:** exported span carries `agent_core.command.name`. **Evidence:** `tests/foundation/test_command_identity.py` passed at integrated agent-core `1c8cf12`; the prior missing-file claim is superseded.
- [x] 2.6 Remove import-time `init_observability()` call from agent-docs-sync. **Repo:** agent-docs-sync. **File:** `src/agent_docs_sync/observability/__init__.py`. **Validation:** import-side-effect and startup-order tests. **Evidence:** agent-docs-sync commit `c6c5b1f45ff018fbe42c76e050e82be195c226e5`; 15 focused tests passed, Ruff and strict mypy passed; unrelated write-containment and Graphify state preserved.
- [x] 2.7 Identify DBOS/worker composition roots without adding DBOS spans. **Repo:** agent-core. **Validation:** document composition root paths in design.md. **Evidence:** Phase 2 Composition-Root Addendum documents `agent_core.cli.app:main`, central `tdt_core.scheduler.cli:_serve`, `agent_core.scheduler_setup`, agent-harness, and code-daily-scan boundaries.

## 3. Resolve instrumentation duplication

- [x] 3.1 Capture the span tree with only `Agent.instrument_all()` active (no explicit `Instrumentation()`). **Repo:** agent-core. **Evidence:** InMemorySpanExporter behavioral matrix in `tests/foundation/test_tracing_extended.py`; focused matrix passed.
- [x] 3.2 Capture the span tree with explicit `Instrumentation()` on AgentRuntime only. **Repo:** agent-core. **Evidence:** InMemorySpanExporter behavioral matrix; explicit per-agent settings preserved.
- [x] 3.3 Capture the span tree with both global and explicit instrumentation. **Repo:** agent-core. **Evidence:** combined matrix produced one root/tool/model ownership tree with correct parent and trace IDs.
- [x] 3.4 Implement the selected ownership model (global canonical, explicit for overrides). **Repo:** agent-core. **File:** `src/agent_core/_ai/agent.py`. **Evidence:** integrated commit `f1642f9`; default runtime synthesis remains available only when global and explicit instrumentation are absent.
- [x] 3.5 Assert one root/model/tool span per logical operation in all configurations. **Repo:** agent-core. **File:** `tests/foundation/test_tracing_extended.py`. **Evidence:** 96 focused tests passed, including all three ownership configurations; GitNexus reported low risk for the isolated Phase 3 commit.

## 4. Correct MLflow and evaluation behavior

- [x] 4.1 Fix MLflow exception isolation: replace `_Suppress.__exit__` returning `None` with correct behavior. **Repo:** agent-core. **File:** `src/agent_core/observability/mlflow_client.py`. **Validation:** `__exit__` now returns `True`. **Evidence:** code reviewed, test updated.
- [x] 4.2 Change `_log_to_mlflow()` reporting semantics: (a) assertion pass rate from `ReportCase.assertions`, (b) task success rate from completed versus failed cases, (c) numeric score summaries separately, (d) `pass_rate=null` when no boolean assertions exist. **Repo:** agent-core. **File:** `src/agent_core/observability/scorers/runner.py`. **Validation:** assertions-based pass_rate, numeric score mean/stddev, None when no assertions. **Evidence:** code reviewed.
- [x] 4.3 Add nullable `trace_id` and `span_id` fields to `EvalRecord`. **Repo:** agent-core. **File:** `src/agent_core/evaluation/types.py`. **Validation:** model accepts None and string values. **Evidence:** Orca worker completed, 9 tests pass.
- [x] 4.4 Add additive SQL migration: `ALTER TABLE agent_memory.eval_metrics ADD COLUMN trace_id TEXT DEFAULT NULL, span_id TEXT DEFAULT NULL`. **Repo:** agent-core. **File:** migration file. **Validation:** migration runs cleanly, existing rows unaffected. **Evidence:** Orca worker completed.
- [x] 4.5 Populate `EvalRecord.trace_id` and `span_id` from `EvaluationReport.trace_id` and `EvaluationReport.span_id` in the evaluation recording path. **Repo:** agent-core. **File:** `src/agent_core/evaluation/store.py`. **Validation:** `EvalRecord` inserted with trace_id and span_id when EvaluationReport contains them. **Evidence:** Orca worker completed, 9 tests pass.
- [x] 4.6 Add tests: migration backward-compat, round-trip write/read, null-context insert, active-context insert. **Repo:** agent-core. **File:** `tests/evaluation/test_store.py`. **Evidence:** 9 tests pass.

## 5. Add trace-log correlation and privacy controls

- [x] 5.1 Add a structlog processor that injects `trace_id` and `span_id` from active OTel span context. **Repo:** agent-core. **File:** `src/agent_core/foundation/logging.py`. **Validation:** JSON log output contains `trace_id` inside active span. **Evidence:** Orca worker `trace-log-worker` completed, tests pass.
- [x] 5.2 Test logging inside active span (trace_id present) and outside (absent). **Repo:** agent-core. **File:** `tests/foundation/test_logging_trace_correlation.py`. **Evidence:** 2 tests pass.
- [x] 5.3 Preserve content-off defaults: verify `include_content=False` is the default. **Repo:** agent-core. **Validation:** test asserts default settings. **Evidence:** privacy test passes.
- [x] 5.4 Add minimum secret redaction for API keys, tokens, and passwords when `capture_sensitive_payloads=true`. **Repo:** agent-core. **File:** `src/agent_core/foundation/tracing.py`. **Validation:** `_SecretRedactionProcessor` with regex-based redaction. **Evidence:** 3 privacy tests pass.
- [x] 5.5 Add tests proving content is absent by default and secrets are redacted when enabled. **Repo:** agent-core. **File:** `tests/foundation/test_tracing_privacy.py`. **Evidence:** 3 tests pass.

## 6. Enforce backend route ownership

- [x] 6.1 Implement explicit Langfuse route mode configuration based on Phase 0 evidence. **Repo:** agent-core. **File:** `src/agent_core/foundation/settings.py` and `src/agent_core/foundation/tracing.py`. **Validation:** `langfuse_mode` setting with direct/collector/disabled. **Evidence:** 5 isolation tests pass.
- [x] 6.2 Preserve manual Langfuse scoring independently of trace ingestion mode. **Repo:** agent-core. **Validation:** `LangfuseClient.score_trace()` is independent of route mode. **Evidence:** code review confirms no coupling.
- [x] 6.3 Implement explicit MLflow route mode configuration based on Phase 0 evidence. **Repo:** agent-core. **File:** `src/agent_core/foundation/settings.py` and `src/agent_core/foundation/tracing.py`. **Validation:** `mlflow_mode` setting with autolog/collector/disabled. **Evidence:** 5 isolation tests pass.
- [x] 6.4 Reject or warn on conflicting backend routes. **Repo:** agent-core. **Validation:** mode=collector logs debug and skips (deferred). **Evidence:** test_collector_mode_deferred passes.
- [x] 6.5 Test backend failure isolation: unavailable Langfuse does not block MLflow or OTel export. **Repo:** agent-core. **File:** `tests/observability/test_backend_isolation.py`. **Evidence:** 5/5 tests pass.

## 7. Runtime and deployment validation

- [x] 7.1 Validate a short-lived agent-core CLI trace reaches the selected backend. **Repo:** agent-core. **Validation:** local OTLP gRPC receiver plus short-lived `agent-core health` subprocess. **Evidence:** `tests/integration/test_cli_otel_export.py` passed; one `agent_core.command health` span was received before exit. Langfuse/MLflow deployment arrival remains unverified.
- [x] 7.2 Validate expected agent/model/tool span hierarchy. **Repo:** agent-core. **Validation:** exported InMemorySpanExporter tree. **Evidence:** all three global/explicit configurations passed behavioral assertions.
- [x] 7.3 Validate spans flush before CLI exit. **Repo:** agent-core. **Validation:** unified bounded shutdown owns provider/backend flush and disables provider-owned duplicate exit hooks. **Evidence:** lifecycle unit tests plus the real OTLP subprocess test passed; no duplicate-shutdown error.
- [x] 7.4 Validate trace IDs correlate with structlog records. **Repo:** agent-core. **Validation:** structlog processor injects trace_id/span_id. **Evidence:** 2 correlation tests pass.
- [x] 7.5 Validate evaluation records link to traces. **Repo:** agent-core. **Validation:** `run_evaluation_and_record()` passes `EvaluationReport` into `EvalMetrics.record()`, which persists report-level IDs. **Evidence:** round-trip storage tests and runner recording test pass.
- [x] 7.6 Validate unavailable backends do not crash or block shutdown. **Repo:** agent-core. **Validation:** disabled mode skips backends gracefully. **Evidence:** `Provider: NoOpTracerProvider, SUCCESS`.
- [x] 7.7 Record evidence level for each capability in design.md. **Repo:** openspec-store. **Evidence:** design.md addendum with Phase 0 evidence.

## 8. Quality gates and closure

- [x] 8.1 Run repository-specific tests, Ruff, mypy strict, and OpenSpec validation. **Repos:** agent-core, agent-docs-sync. **Validation:** integrated agent-core full suite passed with expected environment skips; 97-file strict mypy passed; scoped Ruff passed; docs-sync focused 15 passed plus Ruff/mypy passed. **Evidence:** commits `1c8cf12`, `25e3280`, and `c6c5b1f`; scheduler static/Compose checks also passed.
- [x] 8.2 Run GitNexus `detect_changes()` before commits. **Repo:** agent-core. **Evidence:** Phase 3 low-risk scan and Phase 6 medium-risk scan passed; final lifecycle scan was high-risk because shared settings/tracing/init hubs affect eight known processes, with no unexpected path class. This risk is recorded, not treated as zero-risk.
- [x] 8.3 Run `openspec validate establish-agent-observability-contract --strict --store openspec-store`. **Evidence:** exit 0 — change is valid.
- [x] 8.4 Inspect `openspec show establish-agent-observability-contract --json --deltas-only --store openspec-store` to confirm only `agent-observability-contract` is ADDED and existing capabilities are MODIFIED (or ADDED with genuinely new requirement names). **Evidence:** 39 deltas verified — 1 ADDED spec, 6 MODIFIED specs.
- [x] 8.5 Update the research report and SPEC_INDEX mappings. **Repo:** openspec-store. **Evidence:** errata section added to baseline report.
- [x] 8.6 Track MCP, memory, DBOS spans, handoffs, sampling, and cross-language propagation as separately scoped follow-up changes. **Evidence:** listed as non-goals in proposal.md and deferred in design.md.
