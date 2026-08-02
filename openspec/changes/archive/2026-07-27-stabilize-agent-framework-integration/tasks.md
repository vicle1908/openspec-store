## 1. Establish the Migration Baseline

- [x] 1.1 In `agent-core`, rerun GitNexus impact for `BaseAgent.run`, `AgentRuntime.__init__`, `_build_harness_capabilities`, and `WorkflowEngine.run`; record callers, process families, and the CRITICAL blast-radius checkpoint in the implementation notes.
- [x] 1.2 In `agent-docs-sync`, rerun GitNexus impact for `build_full_engine`, `build_dynamic_orchestrator`, `build_discovery_agent`, `build_doc_sync_agent`, and `WriteDocTool.execute`; record affected CLI paths and the CRITICAL blast-radius checkpoint.
- [x] 1.3 In both repositories, capture `uv lock --check`, installed Pydantic AI/Harness/Monty versions, and the focused integration-test baseline without modifying either lockfile.
- [x] 1.4 Obtain the required dependency-change approval for Pydantic AI 2.18.0, Harness 0.11.0 with `dynamic-workflow`, Monty 0.0.19 from that extra, and LangGraph 1.2.9; stop dependency work if approval is not granted.

## 2. Align and Verify Framework Dependencies

- [x] 2.1 In `agent-core/pyproject.toml`, declare `pydantic-ai>=2.18.0,<2.19`, `pydantic-ai-harness[dynamic-workflow]==0.11.0`, and `langgraph>=1.2.9,<1.3`; remove the direct Monty pin and regenerate `agent-core/uv.lock` with `uv lock`.
- [x] 2.2 In `agent-docs-sync/pyproject.toml`, add direct matching Pydantic AI and Harness-extra dependencies because its source imports both, then regenerate `agent-docs-sync/uv.lock` with `uv lock`.
- [x] 2.3 Run `uv sync --frozen` in both repositories and add a test that requires the exact reviewed tuple `(2.18.0, 0.11.0, 0.0.19, 1.2.9)` in both environments.
- [x] 2.4 Verify every configured public Harness capability imports successfully in both environments, including `DynamicWorkflow`; make import or constructor failures explicit instead of skipping tests.

## 3. Make Capability Activation Faithful

- [x] 3.1 In `agent-core/src/agent_core/_ai/agent.py`, replace silent `_build_harness_capabilities` fallbacks with strict normalization that distinguishes absent, disabled, valid, and invalid configuration.
- [x] 3.2 In `agent-core/src/agent_core/_ai/agent.py`, preserve supplied public capability instances and their constructor policy rather than rebuilding them with permissive defaults.
- [x] 3.3 Update `agent-core` capability tests to assert successful activation by capability type and identity and to assert actionable failures for missing extras, invalid constructors, and unsupported options.
- [x] 3.4 Add regression coverage proving that an explicitly supplied `InputGuard` remains the installed guard and is not replaced by `_allow_all_guard`.
- [x] 3.5 Add regression coverage proving configured capabilities never disappear through a broad `except` path.

## 4. Correct Delegation and Tool Inheritance

- [x] 4.1 In `agent-core`, normalize subagent configuration into public Harness `SubAgent` descriptors with stable names, descriptions, tools, and model inheritance.
- [x] 4.2 In `agent-docs-sync/src/agent_docs_sync/agents/`, update discovery and document-sync delegation to pass valid descriptors instead of raw Pydantic AI `Agent` objects.
- [x] 4.3 Add integration tests that invoke a delegated agent, assert no `resolved_name` failure, and verify the delegated agent receives only its declared tools.
- [x] 4.4 Add a negative test proving invalid or over-authorized subagent definitions fail during construction.

## 5. Make Hooks and Run-Scoped Context Exact

- [x] 5.1 In `agent-core/src/agent_core/agent_base/hooks/`, enforce `tool_filter` before hook invocation and add focused tests for matching and non-matching tool names.
- [x] 5.2 Trace Pydantic AI Hooks, `HookAdapter`, and `HookRegistry` dispatch in `agent-core`; remove duplicate delivery so every framework event reaches a TDT hook exactly once.
- [x] 5.3 Add parity tests for before/after/error tool callbacks, including callback return-value propagation and exactly-once metrics/audit delivery.
- [x] 5.4 In `agent-core`, move selected skills, repository context, correlation data, and invocation metadata into supported per-run dependencies or instructions.
- [x] 5.5 Add two-run isolation tests proving one invocation's skills, context, and correlation data cannot leak into the next invocation.
- [x] 5.6 Add `BaseAgent.run` golden contract tests covering completed output, usage, iteration limits, CLI/example paths, streaming, skills, hooks, and approval results before changing internal dispatch.

## 6. Use Native Deferred Approval Semantics

- [x] 6.1 Inventory current `ApprovalGate`, tool approval metadata, and resume payloads in `agent-core`; map them to Pydantic AI deferred tool call IDs/results and Harness `StepPersistence` run IDs.
- [x] 6.2 Update `agent-core` run and resume paths so `AgentResult` returns an opaque continuation ID, public Harness step storage retains message history, and resume passes native `DeferredToolResults`.
- [x] 6.3 Keep approval authorization in the consumer/TDT policy layer and add tests for approve, deny, stale ID, wrong thread, and unauthorized approver cases.
- [x] 6.4 Remove `_ApprovalResolutionError` and the `approved_tools` side channel from continuation, then test durable restart with a public file/SQLite step store and explicitly process-local behavior with `InMemoryStepStore`.
- [x] 6.5 Add a compatibility test for the current approval projection and document the rollback switch that restores the legacy projection without changing the stable upstream run ID.

## 7. Harden the Docs Consumer Boundary

- [x] 7.1 In `agent-docs-sync/src/agent_docs_sync/guardrails/`, wire the configured input/output guards through `agent-core`, reject write-capable construction without non-empty bounded roots, and add fail-closed prompt-injection and secret-output tests.
- [x] 7.2 In `agent-docs-sync/src/agent_docs_sync/tools/`, centralize write-root resolution and reject traversal, symlink escape, absolute-path escape, and writes outside approved documentation roots.
- [x] 7.3 Enforce the same write boundary at tool preparation, execution, and final output validation; add defense-in-depth tests for all three layers.
- [x] 7.4 Add an audit assertion that every accepted or rejected write records the resolved target, policy decision, and correlation ID without recording secrets.

## 8. Repair Durable Async Workflow Execution

- [x] 8.1 In `agent-core/src/agent_core/orchestration/`, make the workflow runner own the asynchronous checkpointer context for the full compile-and-execute lifetime.
- [x] 8.2 Replace synchronous invocation of async-checkpointed graphs with `ainvoke` or the supported async streaming API and propagate cancellation and errors.
- [x] 8.3 In `agent-docs-sync/src/agent_docs_sync/workflows/`, pass stable thread/checkpoint identifiers through check, update, discover, sync, and audit commands.
- [x] 8.4 Add restart/resume integration tests that pause a docs workflow, close the first runner, reopen durable state, and resume without replaying completed side effects.
- [x] 8.5 Document and test the rollback path to the non-durable in-memory runner when durable storage is unavailable.

## 9. Bound Dynamic Workflow Use

- [x] 9.1 In `agent-docs-sync`, make DynamicWorkflow activation explicit and fail with the missing/incompatible dependency when it is configured but unavailable.
- [x] 9.2 Supply the dynamic scanner with real read-only discovery tools and stable agent metadata; do not grant document-write, shell, or network tools.
- [x] 9.3 Configure finite agent calls, retries, token/usage limits, timeout/resource limits, model inheritance, and deferred loading for the dynamic path.
- [x] 9.4 Add tests that prove the dynamic path discovers work with real tools, respects each bound, and remains optional while the deterministic workflow stays available.

## 10. Verify and Prepare Rollback

- [x] 10.1 Run focused tests for Harness integration, agents, orchestration, hooks, guards, subagents, dynamic workflow, and docs write containment in both repositories.
- [x] 10.2 Run `uv run ruff check .`, `uv run mypy . --strict`, and `uv run pytest -x` in `agent-core` and `agent-docs-sync`; record any unrelated pre-existing failures separately.
- [x] 10.3 Run Graphify queries for the changed framework boundaries and GitNexus `detect_changes` against each repository's default branch; confirm only intended symbols and process families changed.
- [x] 10.4 Exercise the documented rollback sequence: restore the prior dependency constraints and lockfiles together, enable the legacy approval/runner adapters, and verify the deterministic docs workflow still runs.
- [x] 10.5 Update `agent-core` and `agent-docs-sync` integration documentation with supported versions, strict activation errors, authority boundaries, durable-run lifecycle, and migration examples.

## 11. Close Verification Gaps

- [x] 11.1 Reject explicitly empty documentation-root policies in every write-capable agent factory and validate final structured write targets through the output guard.
- [x] 11.2 Restrict durable-to-memory fallback to checkpointer availability failures before workflow execution; propagate workflow failures without replay.
- [x] 11.3 Add a persistent close/reopen checkpoint test that resumes an interrupted workflow without replaying completed side effects.
- [x] 11.4 Lazy-load DynamicWorkflow, keep deterministic workflows importable when the optional capability is unavailable, and provide actionable activation errors.
- [x] 11.5 Execute a bounded DynamicWorkflow with a test model and assert limit failures remain structured without fallback.
- [x] 11.6 Preserve the policy resolver's normalized target in rejected-write audit events and distinguish missing dependencies from incompatible imports in tests.
- [x] 11.7 Rerun frozen dependency checks, focused and full tests, lint/type gates, GitNexus scope detection, and strict OpenSpec verification.

## 12. Prepare for Archive

- [x] 12.1 Make the intentional no-hooks deprecation contract explicit and warning-clean in the `agent-core` test suite.
- [x] 12.2 Refresh final dependency, test, code-intelligence, and strict OpenSpec evidence; record unrelated repository-wide lint/type debt as non-blocking follow-up scope.

## 13. Eliminate Repository-Wide Static-Analysis Debt

- [x] 13.1 Clear every Ruff diagnostic in `agent-core`, including the pre-existing deployment import-order finding.
- [x] 13.2 Clear every strict-mypy diagnostic in `agent-core` without weakening strictness or hiding legitimate errors.
- [x] 13.3 Clear every Ruff diagnostic in `agent-docs-sync`, configuring only conventional test-specific exceptions where the rule is intrinsically incompatible with pytest.
- [x] 13.4 Clear every strict-mypy diagnostic in `agent-docs-sync` without weakening strictness or hiding legitimate errors.
- [x] 13.5 Run the available Python language server over both repositories and resolve all reported errors and warnings attributable to repository source or configuration.
- [x] 13.6 Rerun full tests, frozen dependency checks, GitNexus change detection, strict OpenSpec validation, and archive-readiness evidence.

## 14. Reconcile Verification Drift

- [x] 14.1 Emit a structured capability-activation failure event from `AgentRuntime` with the capability, installed Harness/Monty versions, and actionable remediation.
- [x] 14.2 Align consumer documentation with fail-closed write policy, explicit subagent tools, stable `SubAgent` names, and host-controlled persistence.
- [x] 14.3 Correct implementation paths and post-implementation decisions in the change artifacts, then rerun all archive gates.
