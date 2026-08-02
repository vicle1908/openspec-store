## Context

This change converges `agent-core`, `agent-docs-sync`, and `agent-harness` on the official Pydantic AI, Harness, and LangGraph public contracts. Legacy compatibility adapters have been removed; all consumers now use the typed SDK composition API.

Official Pydantic AI 2.x provides:

- composable capabilities and toolsets;
- full lifecycle Hooks and Instrumentation;
- `PrepareTools`, history and event-stream processing;
- per-run instructions, model/toolset/capability inputs, and supported overrides;
- `Agent.from_file()`/`Agent.from_spec()` with custom capability registration;
- deferred tool requests/results for human decisions.

Pydantic AI Harness provides guardrails, subagents, DynamicWorkflow, memory stores, compaction, output management, repo context, planning, and public step stores. LangGraph provides typed state, native `Command`, interrupts, async execution, checkpointers, and durable thread-based resume.

The execution baseline is Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19 through the Harness `dynamic-workflow` extra, and LangGraph 1.2.9. Public contracts used:

| Concern | Public contract used |
|---|---|
| Agent composition | `AgentCapability`, `AgentToolset`, `FunctionToolset`, run-level `instructions`, `toolsets`, and `capabilities` |
| Tool policy | `PrepareTools` and supported toolset composition |
| Lifecycle | `pydantic_ai.capabilities.Hooks`, `Instrumentation`, `ProcessEventStream`, `ProcessHistory` |
| Human continuation | `DeferredToolRequests`, `DeferredToolResults`, `deferred_tool_results` |
| Agent files | `Agent.from_file`, `Agent.from_spec`, `AgentSpec`, `custom_capability_types` |
| Harness memory | `Memory`, `MemoryStore`, `InMemoryStore`, `FileStore`, `SqliteMemoryStore`, `PostgresMemoryStore` |
| Agent step state | `StepPersistence`, `InMemoryStepStore`, `FileStepStore`, `SqliteStepStore`, and the module-level `pydantic_ai_harness.step_persistence.continue_run` function |
| Workflow state | `StateGraph`, typed schemas/reducers, `Command`, `interrupt`, `ainvoke`, `astream` |

Verified LangGraph contracts:

- `Agent` and `Agent.run` accept `AgentCapability` and `AgentToolset` sequences; run accepts instructions, toolsets, capabilities, model settings, deferred results, and an event-stream handler.
- `Command(resume=...)` accepts either the next interrupt value or a mapping from native interrupt IDs to resume values.
- native `Interrupt` exposes `id`.
- the node containing `interrupt()` re-executes on resume, so artifact generation or non-idempotent validation cannot occur before an interrupt in the same node.
- compiled graphs expose public asynchronous `aget_state` and `aget_state_history` operations for status and audit inspection.
- `AsyncPostgresSaver.setup()` creates/migrates checkpoint tables and must be invoked explicitly before first use.

The converged architecture:

- `agent-core` accepts typed upstream capabilities and toolsets through `agent_core.sdk.build_agent`. The `harness_config` dict, `ConsumerConfig` inheritance, `_build_harness_capabilities` mirror, `HookAdapter` bridge, and `CommandResult` wrapper have been removed.
- `agent-docs-sync` uses one canonical deterministic pipeline (`discover → audit → [generate] → validate → report`). Legacy builder paths have been removed.
- `agent-harness` composes `ConsumerRuntimeProfile` through a domain config, resolves the gateway explicitly, and uses official toolsets/capabilities/hooks. The `HarnessConfig(ConsumerConfig)` inheritance has been removed.

The central architectural boundary:

- upstream libraries own generic agent/workflow mechanics;
- `agent-core` owns TDT gateway/auth integration, policy, budgets, skills, domain tool metadata, audit defaults, and stable consumer composition;
- consumers own domain tools, prompts, state, and workflow topology.

## Goals / Non-Goals

**Goals:**

- Make official capabilities and toolsets first-class public composition inputs.
- Remove private upstream attribute access and exhaustive capability mirroring.
- Preserve TDT-specific policy as small adapters around public protocols.
- Use native Pydantic AI and LangGraph lifecycle, continuation, state, routing, and persistence contracts.
- Consolidate `agent-docs-sync` on one supported deterministic pipeline.
- Migrate `agent-harness` as a second active consumer with explicit gateway, typed composition, and native graph topology.
- Provide an evidence-based promotion rule for future consumer features.

**Non-Goals:**

- Turning `agent-core` into a re-export of every upstream symbol.
- Enabling high-authority capabilities by default.
- Removing centralized gateways, budgets, skills, tool metadata, audit, or resilience policy.
- Rewriting external CLI-based reviewer agents as Pydantic agents.
- Combining unrelated durability layers.
- Promoting consumer stage modules, documentation stages, or graph topology into `agent-core`.
- Creating a generic registry, state-composition DSL, or workflow composer before two consumers prove an identical TDT-specific requirement.

## Decisions

### 1. Public composition uses protocols, not feature-key dictionaries

`agent_core.sdk.build_agent` accepts typed sequences of:

- upstream Pydantic AI `AgentCapability`;
- upstream Pydantic AI `AgentToolset`;
- run-scoped instructions/toolsets;
- TDT policy callbacks or policy objects.

Consumers import those types and concrete capabilities from Pydantic AI/Harness. `agent-core` accepts them but does not re-export upstream concrete types. Small factory helpers may construct common secure TDT profiles, but `agent-core` will not reproduce every upstream constructor argument.

The `harness_config` dict path has been removed. Consumers compose capabilities directly through `build_agent(capabilities=[...], toolsets=[...])`. The `_build_harness_capabilities` mirror and `harness_config` parameter are no longer part of the public API.

Alternative: keep expanding the dictionary. Rejected because every upstream release creates another incomplete schema and silent option loss.

### 2. Tool policy composes through supported toolsets

TDT `BaseTool` and `ToolRegistry` remain the domain-policy boundary. Their Pydantic adapter will expose an official toolset. Per-run allow/deny and skill-derived visibility will use `PrepareTools`, filtered toolsets, or supported `Agent.override`, not private `_function_toolset` access or agent reconstruction.

The adapter must preserve tool schemas, approval metadata, correlation IDs, audit data, and structured `ToolResult` behavior.

### 3. Pydantic AI Hooks are the lifecycle authority

`HookRegistry` has been replaced by the official `Hooks` capability. The full upstream lifecycle—including errors, validation, output processing, and event streaming—is available without a second semantic model. The `HookAdapter` bridge has been removed.

TDT observability remains additive:

- Instrumentation/OTel is the base trace source;
- Langfuse and MLflow consume trace/evaluation events;
- budgets, structured audit, and domain policy remain TDT callbacks.

Duplicate event delivery and adapter-return-value limitations are removed.

### 4. Deferred calls remain native end to end

Tools raise supported approval/defer signals. Runs return the framework's pending requests plus the stable TDT compatibility projection. Resume supplies `deferred_tool_results` directly. No private sentinel exception or `approved_tools` side channel is part of the final design.

LangGraph human-stage interrupts use native `interrupt`/`Command(resume=...)`; tool approval and workflow-stage approval remain separate typed decisions.

### 5. Agent configuration preserves AgentSpec

The file loader delegates construction to `Agent.from_file` or `Agent.from_spec` and supplies:

- model/provider resolution through the TDT gateway factory;
- tool/toolset resolution through a registry;
- registered custom capability types;
- policy validation.

It preserves description, model settings, retries, end strategy, timeouts, metadata, dependency/output schemas, and serializable capabilities. It does not invent a `tools` field absent from `AgentSpec`. Capabilities whose public `get_serialization_name()` is `None`—including Harness `DynamicWorkflow` 0.11.0 because it holds live agents—are supplied through the typed code-composition input, not encoded into YAML.

### 6. Memory uses a Harness store adapter

TDT scratch/context/Postgres behavior remains, but it implements or adapts to `pydantic_ai_harness.memory.MemoryStore`. The official `Memory` capability handles tools and injection limits. Generic local storage uses the public `InMemoryStore`, `FileStore`, `SqliteMemoryStore`, or `PostgresMemoryStore` where their semantics fit. Agent-step continuation uses public `StepPersistence` with `InMemoryStepStore`, `FileStepStore`, or `SqliteStepStore`, then calls the module-level `pydantic_ai_harness.step_persistence.continue_run(store, run_id=...)` helper.

LangGraph checkpoints continue to store workflow state. DBOS continues to own durable scheduled execution. Documentation will include a matrix defining which layer owns which state.

Alternative: replace TDT memory storage entirely. Rejected because existing storage, tenancy, and operational behavior are TDT concerns.

### 7. The LangGraph facade becomes thin and typed

`WorkflowBuilder` may remain as a stable TDT convenience API, but its implementation and public escape hatches use:

- typed state schemas and reducers;
- native node/edge APIs;
- native `Command`;
- native interrupts/resume;
- `ainvoke`/`astream`;
- caller-managed sync or async checkpointer contexts.

Custom `CommandResult` has been removed. All workflow nodes return native LangGraph `Command` or plain dict state updates.

### 8. agent-docs-sync has one pipeline authority

The supported pipeline is deterministic:

`discover → audit → [generate] → validate → report`

Only generation/classification steps may call an agent. One public builder owns tools, policy, hooks, memory, and capability composition. Deprecated discovery/sync/full/dynamic variants are removed after CLI and API migration.

DynamicWorkflow remains optional for bounded adaptive research/classification. It is not used for deterministic file scanning, persistence, or reporting, and it must have real tools, structured outputs, and finite resource/usage limits.

### 9. Consumer adoption is evidence-gated

- `agent-docs-sync` and `agent-harness` are active consumers and form the minimum cross-consumer contract suite.
- `code-daily-scan` currently declares `agent-core` but contains no direct source import. It is not a migration consumer in this change; a separate OpenSpec cleanup must document a packaging/runtime reason or remove the dependency.
- `ai-review` and `jira-epic-report` contain no direct source dependency or import in the current workspace scan and are not framework consumers in this change.
- The `deployments/ai-review/deps/agent-core` tree is a packaged deployment copy, not a separate API consumer; release verification must prove rebuilt artifacts contain the converged source.

A feature is promoted into `agent-core` only if all of the following are true:

1. it is required by at least two active consumers;
2. it implements TDT-owned policy or integration rather than domain topology;
3. no supported public upstream contract already owns the behavior;
4. its API does not import either consumer's domain types;
5. both consumers have contract tests for it.

Otherwise the feature remains consumer-owned. Future pilots require their own OpenSpec change after an execution-flow and ownership assessment.

### 10. Authority remains opt-in

Capabilities with filesystem, shell, code execution, runtime authoring, external search, or network authority require explicit consumer configuration, least-privilege roots/allowlists, finite budgets, and audit events. “Use maximum upstream features” means selecting official implementations for required concerns, not enabling all features.

### 11. Consumer configuration composes a runtime profile

`ConsumerConfig` has been removed. Consumer configuration composes `ConsumerRuntimeProfile` rather than inheriting from a base class. `DocsSyncConfig` and `HarnessConfig` contain it:

```python
class HarnessConfig(BaseModel):
    runtime: ConsumerRuntimeProfile
    gate: GateConfig
    validation: ValidationConfig
    persistence: PersistenceConfig
```

A stage derives changes with immutable copy/update semantics and passes run-specific instructions, toolsets, capabilities, and limits explicitly. This prevents core fields from leaking into domain inheritance trees and makes field removals or renames easier to adapt at one boundary.

Alternative: subclassing `ConsumerConfig`. Rejected because inheritance couples every consumer model to the full core field layout and makes upstream/core migrations breaking by default.

### 12. Consumers own native graph topology

`agent-core` provides only narrow reusable pieces around native LangGraph contracts: typed run context, checkpoint resource factories, TDT telemetry/policy callbacks, and temporary legacy adapters. It does not own a universal `WorkflowComposer`, dynamic state merger, stage registry, or parallel flag.

`agent-docs-sync` and `agent-harness` each declare their `StateGraph` and state schema statically. A consumer-local stage descriptor may package a native node callable, validators, official toolsets/capabilities, and read/write metadata, but topology remains explicit in native graph construction. Parallelism is derived from edges plus safe reducers, not a boolean on a module.

Alternative: promote the proposed harness `WorkflowComposer`, `ToolRegistry`, and `compose_states()` into core. Rejected because LangGraph already owns graph construction/toolset execution semantics, runtime `TypedDict` synthesis is not useful to static type checking, and only one consumer currently needs stage packaging.

### 13. Harness gates and checkpoint resources are end-to-end

Each harness gate is a dedicated post-stage node such as `gate_design` with one continuation. It is not embedded after artifact generation in the stage node because LangGraph re-executes an interrupted node on resume. Gate requests carry run/thread identity, stage, artifact digest, expiry, and authorization context; the returned native `Interrupt.id` is the resume identity. A single shared gate node with edges to every gated stage is prohibited.

The existing `agent_core.sdk.create_async_checkpointer` boundary is extended rather than copied. `agent-core` owns TDT DSN resolution, provisioning through the public `setup()` contract before first use, and saver context lifetime. `WorkflowRunner.run`, `astream`, `resume`, and status inspection receive an opened saver through that boundary, compile with it, and use public compiled-graph state inspection. The thread ID is stable across interruption and process restart, and resume maps `pending_interrupt.id` to its decision. DBOS, if used for scheduled orchestration, does not replace LangGraph workflow checkpoints.

Alternative: compile a fresh in-memory graph for stream/resume. Rejected because it cannot recover a durable pending interrupt.

Alternative: create a harness-local saver factory. Rejected because `agent-core` already exports the factory and `agent-docs-sync` already consumes it, satisfying the two-consumer promotion rule.

## Risks / Trade-offs

- **Public migration surface is large** → introduce typed APIs first, ship adapters and warnings, migrate the active consumer, then remove legacy paths.
- **BaseAgent.run remains CRITICAL** → preserve observable request/result behavior and compare golden traces during each phase.
- **Upstream APIs evolve** → centralize only TDT policy and rely on public protocols; pin/test a compatibility matrix.
- **Typed LangGraph state may require consumer changes** → provide one compatibility state adapter and migration examples.
- **Hook/telemetry migration can duplicate or lose spans** → run exactly-once counter and trace-parent tests before removing adapters.
- **Memory migration can change retrieval semantics** → build parity tests over the same TDT backend before switching the capability.
- **Too many optional capabilities can increase prompt/tool surface** → use stable IDs, deferred loading, explicit profiles, and authority tests.
- **`build_graph` is HIGH and current gates may route incorrectly** → freeze a failing regression fixture first, then replace shared-gate fan-out with stage-specific continuation and compare exact visited-node traces.
- **Configuration composition changes constructor shapes** → add `from_legacy_config` adapters at consumer composition roots for the documented compatibility window; do not retain subclassing internally.
- **Two active changes can encode conflicting architecture** → make `agent-harness-stage-modules` explicitly depend on this change and validate both proposals together before either implementation starts.

## Migration Plan (Completed)

The migration is complete. All 73 tasks across 13 phases have been implemented:

1. ✅ Verified stabilized starting point (framework versions aligned, no silent fallbacks).
2. ✅ Introduced typed SDK composition (`ConsumerRuntimeProfile`, `build_agent(capabilities=..., toolsets=...)`).
3. ✅ Replaced exhaustive capability mirror with typed passthrough.
4. ✅ Migrated lifecycle ownership to official Hooks capability.
5. ✅ Finished native deferred and stream integration.
6. ✅ Made agent specifications round-trip faithfully.
7. ✅ Adopted Harness memory stores (`TDTMemoryStore` adapter).
8. ✅ Thinned the LangGraph facade (native `Command`, typed state, checkpointers).
9. ✅ Consolidated docs consumer on one deterministic pipeline.
10. ✅ Validated additional consumers (census, contract tests, promotion checklist).
11. ✅ Migrated harness consumer (explicit gateway, typed composition, native graph).
12. ✅ Removed compatibility surfaces (deprecation warnings, manifest census, release checks).
13. ✅ Verified convergence (lint, typecheck, tests, Graphify, rollback, compatibility matrix).

Rollback: the typed composition path is the only supported path. Legacy paths have been removed. Harness graph rollout uses the shared core checkpointer boundary with native interrupt-ID mapping. No data migration is destructive.

Deployment is by normal package/source release and Docker rebuild for deployed consumers.

## Resolved Execution Decisions

- Legacy compatibility adapters (`harness_config`, `ConsumerConfig` inheritance, `HookAdapter`, `CommandResult`) have been removed. The typed SDK composition API is the only supported path.
- Consumers import official capability/toolset types from upstream packages; `agent_core.sdk` accepts them without re-exporting concrete upstream classes.
- `code-daily-scan` is not an integration pilot; its unused dependency is handled by a separate cleanup change after packaging ownership is verified.
- `agent-harness` is an active integration consumer, and `agent-harness-stage-modules` depends on this convergence change.
- Stage packaging remains consumer-local until another active consumer demonstrates the same stable requirement.
