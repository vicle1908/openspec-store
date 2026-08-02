## Context

The change spans `agent-core` and its active consumer `agent-docs-sync`.

Research against live source, refreshed GitNexus indexes, Graphify graphs, Context7 documentation, and the installed packages established the following:

- `agent-core` resolves Pydantic AI 2.18.0, Harness 0.10.0, and Monty 0.0.18.
- `agent-docs-sync` resolves Harness 0.11.0 while pinning Monty below 0.0.19; Harness 0.11 declares `pydantic-monty>=0.0.19` for DynamicWorkflow. The import consequently fails on `MontyCrashedError`, the consumer silently omits the capability, and three tests skip.
- A configured `InputGuard` instance is treated as a non-callable and replaced by an allow-all guard.
- Raw Pydantic `Agent` instances passed to Harness `SubAgents` fail because Harness requires `SubAgent` descriptors.
- DynamicWorkflow scanner/classifier/saver agents have zero tools.
- `HookRegistry.tool_filter` is recorded but not evaluated.
- `BaseAgent.run` resolves skills but only applies their tool allowlist; instructions are not added to that run.
- the approval bridge interrupts native deferred handling and resumes from messages without approved/rejected deferred results.
- docs writes do not enforce their root at the tool boundary.
- `build_full_engine(durable=True)` returns after closing its saver, while `WorkflowEngine.run` calls synchronous `invoke` around async handlers.

The current targeted tests pass because they verify construction/private attributes and, in two integration suites, catch every exception. Stabilization therefore requires behavioral contract tests rather than more construction-only coverage.

GitNexus classifies `BaseAgent.run` and `build_full_engine` as CRITICAL blast-radius symbols. Implementation must be staged and must preserve their public result/CLI contracts.

## Goals / Non-Goals

**Goals:**

- Establish one tested dependency compatibility set for both repositories.
- Make every explicitly requested capability either active and testable or fail with an actionable error.
- Restore safe guardrails, delegation, write containment, hooks, per-run skills, approval continuation, DynamicWorkflow, and durable workflow execution.
- Preserve current `BaseAgent`, `AgentRequest`, `AgentResult`, CLI, tool metadata, gateway, budget, and observability contracts where they are not defective.
- Produce contract tests that exercise real framework behavior with test models and disposable persistence.

**Non-Goals:**

- Removing all custom composition layers; that belongs to `converge-agent-framework-upstream`.
- Adding consumers beyond `agent-docs-sync`.
- Enabling Shell, CodeMode, RuntimeAuthoring, or unrestricted DynamicWorkflow.
- Changing mobile applications, Jira/GitLab clients, or deployment topology.

## Decisions

### 1. Align on the current compatible upstream family

Both repositories will use one reviewed compatibility family:

- `pydantic-ai>=2.18.0,<2.19`;
- `pydantic-ai-harness[dynamic-workflow]==0.11.0`;
- `pydantic-monty==0.0.19` as the lockfile resolution selected by the Harness extra, not as a hand-maintained direct dependency;
- `langgraph>=1.2.9,<1.3`.

These are the current PyPI releases and match the installed Pydantic AI/LangGraph APIs used by the design. `agent-docs-sync` imports Pydantic AI and Harness directly, so it will declare those direct dependencies rather than rely on `agent-core` transitively. Both committed lockfiles must resolve the exact baseline above. The mandatory dependency-review checkpoint remains the first implementation gate.

The implementation will remove the stale Monty `<0.0.19` constraint after verifying that TDT source does not directly rely on the removed `MontyRepl` API. `uv sync --frozen`, public-import probes, and identical version probes in both repositories will be release gates.

Alternative: pin both repositories to Harness 0.10/Monty 0.0.18. Rejected because it would restore DynamicWorkflow but deliberately remain behind the official feature set the workspace wants to adopt.

### 2. Explicit capability requests fail closed

The transitional `harness_config` interface remains during stabilization, but its normalization rules become strict:

- a guard callable is wrapped in the corresponding Harness guard;
- an already-built Harness capability is preserved as-is;
- subagent configuration accepts valid `SubAgent` descriptors;
- requested optional capabilities that cannot import raise a typed configuration error containing the `uv add`/version remediation;
- public Harness exports are used for step stores;
- broad `except Exception: pass` paths are removed from capability construction.

Optional capabilities that are absent from configuration remain disabled without error.

Alternative: preserve silent degradation for availability. Rejected because safety and durability features cannot safely degrade to no-ops.

### 3. Run-scoped data stays run-scoped

`AgentRuntime.run` and streaming/resume equivalents will accept run-scoped instructions and context. `BaseAgent.run` will:

1. resolve skills;
2. build skill instructions without mutating the base agent;
3. copy `AgentRequest.context` into runtime dependencies using an explicit allowlist for policy keys;
4. pass the run-scoped instructions through the supported Pydantic AI run API.

This avoids instruction leakage and agent reconstruction.

### 4. HookRegistry remains temporarily, with one dispatch authority

During stabilization, `HookRegistry` stays public. Pydantic AI Hooks, through the adapter, become the single delivery path for agent lifecycle events. `BaseAgent.run` will not emit duplicate RUN callbacks around the same inner run.

`HookRegistry` will enforce `tool_filter` before invocation for before, after, and error phases. Tests will cover matching and non-matching tools and exactly-once run/model/tool events.

Alternative: remove HookRegistry immediately. Rejected because consumers and observability packs require a compatibility migration.

### 5. Approval state uses native deferred identifiers

Approval requests will retain the upstream tool-call identifier and metadata needed to construct `DeferredToolResults`. `AgentResult` will expose the pending requests plus an opaque `continuation_id` equal to the stable upstream run ID; it will not serialize framework message objects into the public result.

The runtime will install Harness `StepPersistence` with a public `StepStore` for resumable approval runs. A durable file/SQLite store is required when continuation must survive a process restart; an `InMemoryStepStore` is permitted only for explicitly process-local execution. Resume will load the stored message history through the public continuation API, accept explicit approve/reject decisions, build native `DeferredToolResults`, and call Pydantic AI with `message_history` and `deferred_tool_results`. Rejected calls will return structured rejection results; approved calls will execute once. Private sentinel exceptions and the `approved_tools` side channel will no longer be continuation mechanisms.

Authorization remains a consumer concern: callers must validate approver identity before passing a decision. No Jira/GitLab approval transport is added.

### 6. Documentation writes use defense in depth

Allowed roots will be normalized relative to an explicit workspace root and propagated through `AgentRequest.context`. Construction of a write-capable docs agent will fail when no non-empty bounded root policy is supplied. The validation hook will also fail closed if run-scoped write policy is missing.

`WriteDocTool` and `SyncSpecTool` will independently resolve the target, reject traversal/symlink escapes, and require containment before creating directories or writing. Approval metadata remains mandatory but is not treated as a substitute for containment.

### 7. Durable workflow resource lifetime belongs to the runner

`WorkflowEngine.run` and resume will use `ainvoke`/async streaming as appropriate. Graph compilation may be cached per engine, but it must not outlive the checkpointer resource supplied to it.

`build_full_engine` will become resource-neutral. The runner/CLI will enter the saver context, build the engine, execute or resume, and exit only after the operation completes. Tests will use disposable savers and assert checkpoint recovery by `thread_id`.

DBOS agent durability, Harness step persistence, and LangGraph checkpointing remain distinct mechanisms with documented ownership.

### 8. DynamicWorkflow is optional but never fictional

The deterministic docs-sync DAG remains the primary workflow. If DynamicWorkflow is enabled:

- the compatible extra must import;
- each workflow agent must receive only the read-only tools needed for its
  declared action;
- persistence must remain a deterministic host-controlled step outside the
  model-authored workflow;
- `max_agent_calls`, subagent `UsageLimits`, retry count, and `WorkflowResourceLimits` must be finite;
- initialization or execution failure must be surfaced;
- tests must execute at least one bounded workflow using a test model.

### 9. Error handling and observability

Typed configuration/dependency errors will include the capability name and
remediation without exposing secrets. Capability activation failures will also
emit a structured event containing the installed Harness and Monty versions.
Existing structlog/OTel instrumentation remains. Approval pauses, rejected
writes, workflow resumes, and fallback decisions will emit structured events.

## Risks / Trade-offs

- **CRITICAL BaseAgent blast radius** → preserve `AgentRequest`/`AgentResult`, add golden contract tests for examples, CLI, skills, hooks, approvals, and streaming before changing dispatch.
- **CRITICAL docs-sync CLI blast radius** → repair checkpointer ownership behind the existing CLI flags and test every CLI route that reaches `run_full_dag`.
- **Dependency update may expose upstream changes** → require explicit review, update one repository first, run the full gate, then align the second lockfile.
- **Fail-closed behavior can surface latent misconfiguration** → provide precise error messages and a preflight capability diagnostic.
- **Write containment can reject formerly accepted relative paths** → normalize against an explicit workspace root and document migration examples.
- **Exactly-once hooks can change metric counts** → add counter assertions and note the correction in release documentation.
- **Graph indexes under-report cross-repo callers** → supplement GitNexus with consumer contract tests and repository-wide import scans.

## Migration Plan

1. Obtain dependency-version review and select the exact compatible Pydantic AI/Harness/Monty set.
2. Align `agent-core`, run its full lint/type/test gates, and publish the tested contract.
3. Add strict capability normalization and behavior-level tests.
4. Repair run-scoped skills/context, hook filtering/delivery, and native approval continuation.
5. Align `agent-docs-sync` dependencies and replace exception-swallowing tests.
6. Add contained write tools and durable async workflow ownership.
7. Enable and execute the bounded DynamicWorkflow integration test.
8. Run cross-repository contract tests, GitNexus `detect-changes`, and strict OpenSpec validation.
9. Update integration documentation and unblock the convergence change.

Rollback uses the last compatible lockfiles and retains the old public `AgentRequest`/`AgentResult` shapes. Capability requests must not be silently downgraded during rollback; incompatible optional features remain explicitly unavailable.

Deployment is a normal source/package update. Rebuild any Docker consumer with `docker compose up --build -d`; no database migration or launchd change is planned.

## Resolved Execution Decisions

- The dependency-review candidate is Pydantic AI 2.18.0, Harness 0.11.0 with its `dynamic-workflow` extra, Monty 0.0.19 from that extra, and LangGraph 1.2.9.
- `AgentResult` carries an opaque continuation ID; public Harness step persistence owns resumable message history.
- A write-capable docs agent without a bounded root policy fails during construction, and every write is checked again at execution.
