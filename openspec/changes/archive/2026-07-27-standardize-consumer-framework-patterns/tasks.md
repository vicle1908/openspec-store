## 1. agent-core: Fix build_toolkit bug

- [x] 1.1 Add `hooks: HookRegistry | None = None` attribute to `ToolRegistry` class in `agent-core/src/agent_core/tool_registry/registry.py`
- [x] 1.2 Update `build_toolkit()` in `agent-core/src/agent_core/sdk/tools.py` to attach populated `HookRegistry` to returned `ToolRegistry`
- [x] 1.3 Add test for `build_toolkit` with hooks in `agent-core/tests/sdk/test_tools.py`
- [x] 1.4 Run `uv run pytest tests/sdk/test_tools.py -x` to verify

## 2. agent-core: Extend build_agent helper

- [x] 2.1 Add `hooks: HookRegistry | None = None` and `harness_config: dict[str, Any] | None = None` params to `build_agent()` in `agent-core/src/agent_core/sdk/agents.py`
- [x] 2.2 Implement Tier 0 auto-registration: when `hooks` is provided but empty, call `register_pack(hooks, "otel_metrics")` and `register_pack(hooks, "structured_audit")`
- [x] 2.3 Pass `hooks` and `harness_config` through to `BaseAgent` constructor
- [x] 2.4 Add test for `build_agent` with empty hooks (verify Tier 0 auto-registration) in `agent-core/tests/sdk/test_agents.py`
- [x] 2.5 Add test for `build_agent` with pre-populated hooks (verify no double-registration)
- [x] 2.6 Add test for `build_agent` with `harness_config`
- [x] 2.7 Run `uv run pytest tests/sdk/test_agents.py -x` to verify

## 3. agent-docs-sync: Migrate agent builders to use build_agent

- [x] 3.1 Refactor `agent-docs-sync/src/agent_docs_sync/agents/discovery.py:build_discovery_agent()` to use `build_agent()` SDK helper instead of manual `BaseAgent` construction
- [x] 3.2 Refactor `agent-docs-sync/src/agent_docs_sync/agents/generation.py:build_generation_agent()` to use `build_agent()` SDK helper
- [x] 3.3 Refactor `agent-docs-sync/src/agent_docs_sync/agents/validation.py:build_validation_agent()` to use `build_agent()` SDK helper
- [x] 3.4 Verify `agent.py:build_doc_sync_agent()` still works (it has complex flavor/hook logic — may keep manual construction but ensure Tier 0 hooks are registered)
- [x] 3.5 Run `uv run pytest tests/ -x` in agent-docs-sync to verify all agents build correctly

## 4. agent-docs-sync: Standardize hook registration

- [x] 4.1 Ensure `agents/generation.py:build_generation_agent()` registers `otel_metrics` and `structured_audit` via `register_pack`
- [x] 4.2 Ensure `agents/discovery.py:build_discovery_agent()` registers `otel_metrics` and `structured_audit` via `register_pack`
- [x] 4.3 Ensure `agents/validation.py:build_validation_agent()` registers `otel_metrics` and `structured_audit` via `register_pack`
- [x] 4.4 Verify `agent.py:build_doc_sync_agent()` already has both Tier 0 packs (it does — confirm)
- [x] 4.5 Run `uv run pytest tests/ -x` to verify

## 5. agent-docs-sync: Consolidate pipelines to WorkflowEngine

- [x] 5.1 Update `agent-docs-sync/src/agent_docs_sync/cli.py` entry points to use `full_dag.py` for sync --full, keep working pipelines for check/update/audit
- [x] 5.2 Add deprecation warnings to `full_pipeline.py:run_full_pipeline()` and `full_pipeline.py:run_full_audit()`
- [x] 5.3 Add deprecation warnings to `sync_pipeline.py:build_sync_pipeline()`
- [x] 5.4 Add deprecation warnings to `discovery_pipeline.py:run_discovery_pipeline()`
- [x] 5.5 Keep `dynamic_pipeline.py` as-is (optional advanced pattern, documented in README)
- [x] 5.6 Run `uv run pytest tests/ -x` to verify CLI entry points work

## 6. agent-docs-sync: Documentation

- [x] 6.1 Update `agent-docs-sync/README.md` with consumer pattern guide: when to use `build_agent` vs manual `BaseAgent`
- [x] 6.2 Add section explaining hook tiers (Tier 0/1/2) and when to use each
- [x] 6.3 Add section explaining DynamicWorkflow vs WorkflowEngine (when to use each)
- [x] 6.4 Verify all changes pass `uv run ruff check . && uv run mypy src/ --strict`

## 7. Verification

- [x] 7.1 Run full test suite in agent-core: `cd agent-core && uv run pytest -x`
- [x] 7.2 Run full test suite in agent-docs-sync: `cd agent-docs-sync && uv run pytest -x`
- [x] 7.3 Run lint/typecheck in both repos
- [x] 7.4 Verify `from agent_core.sdk import build_agent, build_toolkit` works from agent-docs-sync
- [x] 7.5 Verify no regressions in existing agent builds
