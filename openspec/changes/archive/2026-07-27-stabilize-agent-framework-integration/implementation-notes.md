# Implementation Notes

## Baseline gate (2026-07-27)

Tasks 1.1–1.3 were completed read-only. No project manifest or lockfile was
modified.

### GitNexus impact: `agent-core`

The refreshed `agent-core` index is dated 2026-07-27 and reports:

| Symbol | UID | Risk | Impact | Direct callers | Processes / modules |
|---|---|---:|---:|---|---|
| `BaseAgent.run` | `Method:src/agent_core/agent_base/agent.py:BaseAgent.run#4` | **CRITICAL** | 27 symbols (d1=21, d2=5, d3=1) | CLI `_run_agent_prompt`, code-review adapter, examples, and 17 behavior tests among 21 direct references | 5 process families (`review_mr`, CLI `_run_agent_prompt`, and four example/main flows); 5 modules (`Agent_base`, `Tool_registry`, `Code_reviewer`, `Examples`, `Hooks`) |
| `AgentRuntime.__init__` | `Method:src/agent_core/_ai/agent.py:AgentRuntime.__init__#8` | LOW | 0 upstream symbols | No upstream callers in the index; it owns `_build_harness_capabilities` | 2 local constructor process traces; no affected modules |
| `_build_harness_capabilities` | `Method:src/agent_core/_ai/agent.py:AgentRuntime._build_harness_capabilities#1` | **HIGH** | 20 direct references | `AgentRuntime.__init__` plus 19 durability/Harness integration tests | Constructor process (`__init__`); 2 modules (`Tests`, `Foundation`) |
| `WorkflowEngine.run` | `Method:src/agent_core/orchestration/graph.py:WorkflowEngine.run#2` | **HIGH** | 17 symbols (d1=15, d2=1, d3=1) | Workflow example plus 14 orchestration tests among 15 direct references | No indexed process family; `Orchestration` module |

The **CRITICAL/HIGH** ratings are an implementation approval gate. Changes to
these symbols must preserve the existing public `AgentRequest`, `AgentResult`,
CLI, example, streaming, hook, and orchestration contracts.

### GitNexus impact: `agent-docs-sync`

The refreshed `agent-docs-sync` index is dated 2026-07-27 and reports:

| Symbol | UID | Risk | Impact | Direct callers | Affected CLI / modules |
|---|---|---:|---:|---|---|
| `build_full_engine` | `Function:src/agent_docs_sync/workflows/full_dag.py:build_full_engine` | **CRITICAL** | 8 symbols (d1=1, d2=1, d3=6) | `run_full_dag` | `discover`, `check`, `sync`, `audit`, and `update`; `Agent_docs_sync` |
| `build_dynamic_orchestrator` | `Function:src/agent_docs_sync/workflows/dynamic_pipeline.py:build_dynamic_orchestrator` | LOW | 1 direct symbol | `run_dynamic_discovery` | `Workflows` |
| `build_discovery_agent` | `Function:src/agent_docs_sync/agents/discovery.py:build_discovery_agent` | LOW | 0 upstream symbols | No indexed callers; local dependencies include validator subagent and input guard construction | No upstream process/module |
| `build_doc_sync_agent` | `Function:src/agent_docs_sync/agent.py:build_doc_sync_agent` | LOW | 0 upstream symbols | No indexed callers | No upstream process/module |
| `WriteDocTool.execute` | `Method:src/agent_docs_sync/tools/write_doc.py:WriteDocTool.execute#1` | LOW | 2 direct symbols | `test_write_doc_overwrite`, `test_write_doc_append` | `Tools` |

The `build_full_engine` **CRITICAL** rating covers every CLI route that reaches
`run_full_dag`; durable-resource changes require CLI contract and resume tests.

### Dependency and test baseline

The latest-release check on 2026-07-27 (Context7 library resolution plus the
PyPI package metadata) reports the same reviewed tuple: Pydantic AI 2.18.0,
Harness 0.11.0, Monty 0.0.19, and LangGraph 1.2.9.

Before the manifest edit, `uv lock --check` passed in both repositories:

- `agent-core`: Pydantic AI 2.18.0, Harness 0.10.0, Monty 0.0.18, LangGraph 1.2.9.
- `agent-docs-sync`: Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.18, LangGraph 1.2.9.

Focused tests were run with `PYTHONDONTWRITEBYTECODE=1` and
`-p no:cacheprovider`:

- `agent-core`: 69 tests passed (`test_harness_integration.py`,
  `tests/agent_base/test_agent.py`, and
  `tests/orchestration/test_orchestration.py`).
- `agent-docs-sync`: 52 passed, 3 skipped
  (`test_guardrails_integration.py`, `test_subagents_integration.py`,
  `test_dynamic_workflow.py`, and `test_workflow.py`). The three skips are
  the known incompatible DynamicWorkflow/Monty baseline and must not remain
  skips after the reviewed dependency alignment.

After the dependency alignment, the exact-tuple/public-import tests pass in both
repositories; the focused suites pass with 70 tests in `agent-core` and 56
tests in `agent-docs-sync`. DynamicWorkflow no longer skips or fails during
construction.

### Capability activation stage

- Explicit capability configuration is validated as a mapping and fails with
  `ConfigError` instead of disappearing.
- Every optional Harness import path now raises an actionable `uv` remediation
  when the requested capability cannot load.
- Guard configuration preserves supplied `InputGuard`/`OutputGuard` instances;
  no allow-all guard is synthesized.
- Step stores come from the public `pydantic_ai_harness.step_persistence`
  surface.
- Subagent catalogs accept public `SubAgent` descriptors and reject raw
  Pydantic `Agent` instances.
- Consumer factories return stable `validator` and `planner` descriptors.
- A Pydantic model-field default lookup defect discovered by the now-strict
  consumer construction test was repaired in `ConsumerConfig.from_env`.

### Hook stage

- `HookRegistry` evaluates `tool_filter` for before, after, and error tool
  lifecycle phases.
- RUN hooks are delivered only through the Pydantic AI `Hooks` adapter; the
  duplicate outer `BaseAgent.run` dispatch was removed.
- Request context is copied into run dependencies with reserved runtime keys
  applied last, so consumer fields cannot overwrite run identity or registry
  state.
- Tool before/after/error callbacks now have execution-level parity tests for
  value propagation, recovery, filtering, and exactly-once delivery.

### Delegation stage

- `agent-core` forwards the reviewed public `SubAgents` 0.11 controls and
  rejects unknown options instead of silently ignoring them.
- The discovery and document-sync factories install explicit bounded
  `SubAgent` descriptors with stable names, finite usage/time/call limits,
  parent-tool inheritance disabled, and ambient disk-agent loading disabled.
- The consumer rejects raw agents, inherited parent tools, and ambient agent
  folders during construction.
- An execution-level `delegate_task` test completed without a `resolved_name`
  error and observed only the child's declared read tool; the parent's write
  tool was absent from the child model request.
- Exercising the previously untested document-sync factory also exposed and
  repaired two API-drift defects: duplicate registration of the built-in
  `git_diff` tool and use of the removed `build_agent(model=...)` argument.
- GitNexus reports the consumer change as MEDIUM (one discovery construction
  flow). The cumulative framework change remains CRITICAL because it includes
  the previously approved `BaseAgent.run` contract work.

### Run-scope stage

- Selected skill bodies are supplied through Pydantic AI's public per-run
  `instructions=` argument. The base agent is not reconstructed or mutated.
- Only approved request-context keys are promoted into `AgentRuntimeDeps`;
  reserved run identity, agent, model, registry, and budget fields are applied
  by the framework and cannot be overridden by consumer context.
- Active skill names, repository/write policy context, correlation data, and
  invocation metadata are available to hooks and tools for that invocation.
- A two-run test uses different skills, roots, metadata, and correlation IDs
  and proves neither instructions nor dependency context leaks across runs.
- `BaseAgent.run` now preserves the runtime's public usage object in its result.
  Golden coverage includes completed output/usage, iteration caps, hooks,
  approvals, streaming, CLI routes, skill dispatch, and importable example
  entrypoints.

### Native approval stage

- The previous path generated a second approval ID, raised
  `_ApprovalResolutionError`, stored requests in `deps.extra`, and used the
  `approved_tools` side channel during resume. The only existing resume API
  accepted an already-loaded snapshot and never supplied native deferred
  results.
- The replacement exposes Pydantic AI's tool-call ID as the default request
  ID, returns the upstream run ID as `AgentResult.continuation_id`, and maps
  authorized decisions to `DeferredToolResults`/`ToolDenied`.
- Every runtime owns a public Harness `StepPersistence` store. An unresolved
  approval frontier is saved explicitly with the public
  `ContinuableSnapshot` API because Harness records the run/events but does
  not automatically snapshot unsettled deferred calls.
- `BaseAgent.resume` verifies authorization, continuation association,
  pending IDs, and conversation/thread identity before executing. Consumer
  code remains responsible for authenticating the actor before setting
  `ApprovalDecision.authorized=True`.
- Both built-in and custom consumer tools now pass through the same native
  approval adapter. Approved tools execute once; denied tools do not execute.
- File-backed persistence resumes in a new runtime. `InMemoryStepStore` is
  explicitly tested as process-local.
- `harness_config={"approval_projection": "legacy"}` restores deterministic
  `appr-*` public request IDs while preserving the same continuation ID and
  mapping back to the native tool-call ID. The default is `"native"`.

The repositories already contained unrelated dirty files before this change;
they were preserved.

### Consumer containment stage

- Write-capable factories install official Harness `InputGuard` and
  `OutputGuard` capabilities through `agent-core`.
- A shared path policy resolves the workspace, approved relative roots, target
  traversal, and symlinks before either `WriteDocTool` or `SyncSpecTool` can
  create a directory or file.
- The same policy runs in the tool-preparation hook and the tool itself; prompt
  injection and secret-like final output are blocked by the public guards.
- Accepted and rejected audit records contain the resolved target, decision,
  correlation ID, and mode/dry-run only. Tests prove document content and
  secret values are absent.

### Durable workflow stage

- `WorkflowEngine.run` and `resume` now use LangGraph `ainvoke`, preserving
  async cancellation and checkpointer errors.
- `create_async_checkpointer` exposes `AsyncPostgresSaver` with an async
  context lifetime spanning compile and execute.
- The docs runner owns that context, calls saver setup, and supplies a stable
  thread/checkpoint ID. CLI check, update, discover, sync, and audit routes
  derive stable identifiers from command plus resolved repository.
- A second workflow runner resumes the same stored thread without replaying a
  completed side effect.
- `fallback_to_memory=True` is the explicit rollback when durable storage is
  unavailable; direct durable engine construction without an active saver
  fails with an actionable error.

### Dynamic workflow stage

- Dynamic activation is explicit and no longer disappears behind import or
  constructor exceptions.
- The dynamic catalog contains bounded stale-check, scanner, GitNexus,
  Graphify, classifier, and reporting agents. It exposes no document-write,
  shell, or network tools.
- Harness enforces finite calls, retries, sub-agent request/token usage,
  inherited model choice, deferred loading, and Monty memory/CPU limits.
- Tests execute the real scanner function, inspect the exact read-tool set and
  bounds, and prove `enable_dynamic=False` leaves the deterministic path
  available.

### Final verification (superseded by archive-readiness verification below)

- Exact dependency tuple: Pydantic AI 2.18.0, Harness 0.11.0,
  Monty 0.0.19, LangGraph 1.2.9; `uv sync --frozen` succeeds in both repos.
- Full tests: `agent-core` passed 535 tests; `agent-docs-sync` passed
  184 tests.
- `openspec validate --strict stabilize-agent-framework-integration` passes.
- Graphify indexes were rebuilt and queries resolve the native approval,
  async checkpointer, write-containment, and dynamic-workflow boundaries.
- GitNexus reports CRITICAL cumulative scope in both repositories, expected
  from the approved `BaseAgent.run` and CLI workflow process families.
- Full Ruff remains blocked only by one pre-existing import-order finding in
  `agent-core`; `agent-docs-sync` retains its pre-existing lint backlog.
- Strict mypy remains a repository-wide backlog (169 findings in `agent-core`,
  260 in `agent-docs-sync`, dominated by existing test annotations and
  untyped cross-repo imports); the changed framework runtime paths pass a
  focused strict-mypy run plus focused test and Ruff coverage.
- Rollback switches were exercised by the native-approval legacy projection,
  disabled dynamic capability, and non-durable deterministic runner tests.
  Dependency rollback is documented as an atomic constraint-and-lockfile
  restore rather than leaving a mixed generation.

### Archive-readiness verification

- The intentional no-hooks compatibility path is covered with an explicit
  `pytest.warns` assertion, so the full `agent-core` suite remains warning-clean
  while preserving the deprecation contract.
- At this checkpoint, repository-wide Ruff and strict-mypy findings outside
  the changed integration paths were recorded as separate technical debt. The
  later repository-wide remediation section supersedes that interim scope
  decision after the user explicitly expanded this change.
- The dependency, full-suite, GitNexus, and OpenSpec results below are refreshed
  immediately before archive preparation; the earlier counts are retained only
  as historical implementation-stage evidence.
- Frozen dependency resolution and synchronization pass in both repositories
  with Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19, and LangGraph 1.2.9.
- Full suites pass warning-clean: 536 tests in `agent-core` and 192 tests in
  `agent-docs-sync`.
- GitNexus reports the expected approved CRITICAL cumulative scope:
  `agent-core` changes 22 files/103 symbols across 56 processes, and
  `agent-docs-sync` changes 29 files/131 symbols across 59 processes.
- The then-remaining static-analysis baseline was one Ruff import-order finding
  and 167 strict-mypy findings in `agent-core`, plus 322 Ruff findings and 270
  strict-mypy findings in `agent-docs-sync`. These historical counts were
  subsequently cleared in the repository-wide remediation stage below.
- `openspec validate --strict stabilize-agent-framework-integration` passes
  with all 55 tasks complete. The change is ready for the archive workflow; it
  has not been archived by this preparation step.

### Repository-wide static-analysis remediation

- All pre-existing Ruff findings were addressed. Both repositories now pass
  `uv run ruff check .` with zero diagnostics.
- Both repositories now pass `uv run mypy . --strict`. Production code remains
  fully strict; narrowly scoped test-only overrides keep test bodies checked
  while accommodating deliberately structural mocks and pytest fixtures.
- Both repositories now include a Pyright workspace configuration covering
  production source. Pyright 1.1.411 reports zero errors and zero warnings.
- `agent-core` now ships a PEP 561 `py.typed` marker. Consumer analysis therefore
  uses the framework's public types, which exposed and corrected SDK annotations
  for `Self`-returning configuration constructors, `ToolRegistry` input,
  `ResilientGateway`, and asynchronous workflow handlers.
- The async workflow wrapper now preserves coroutine handlers and normalizes
  `CommandResult` only after awaiting them, matching LangGraph's native async
  execution contract.
- Frozen dependency checks and full suites pass after remediation: 536 tests in
  `agent-core` and 192 tests in `agent-docs-sync`.
- Final GitNexus cumulative scope remains CRITICAL as expected for the approved
  integration: 33 files/131 symbols/69 processes in `agent-core`, and
  60 files/256 symbols/85 processes in `agent-docs-sync`.
- With tasks 13.1–13.6 complete, the change has 61 completed tasks and remains
  ready for archive.

### Final reconciliation verification

- `AgentRuntime` now emits `capability_activation_failed` with capability,
  stable error code, installed Harness/Monty versions, and remediation before
  re-raising the typed configuration error.
- Active integration documentation and change artifacts now match the
  implementation's fail-closed write policy, explicit child-tool authority,
  stable `SubAgent` descriptors, and host-controlled persistence boundary.
- Frozen dependency resolution remains Pydantic AI 2.18.0, Harness 0.11.0,
  Monty 0.0.19, and LangGraph 1.2.9 in both repositories.
- Full archive gates pass: Ruff and formatting report zero diagnostics, strict
  mypy succeeds, and Pyright reports zero errors and zero warnings.
- Full suites pass after reconciliation: 537 tests in `agent-core` and 192
  tests in `agent-docs-sync`.
- GitNexus reports the expected approved CRITICAL cumulative scope:
  `agent-core` changes 36 files/136 symbols across 69 processes, and
  `agent-docs-sync` changes 61 files/267 symbols across 85 processes.
- Strict OpenSpec validation passes with 21 requirements, 56 scenarios, and
  all 64 tasks complete. The change is ready for archive.
