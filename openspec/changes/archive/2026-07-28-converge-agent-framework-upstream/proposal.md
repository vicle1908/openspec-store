## Why

`agent-core`, `agent-docs-sync`, and `agent-harness` exposed overlapping agent, tool, configuration, hook, state, and workflow abstractions. Without an explicit promotion rule, each consumer could either duplicate framework mechanics or push domain-specific concepts into `agent-core`, increasing upgrade cost and making upstream Pydantic AI, Harness, and LangGraph changes harder to adopt safely.

## What Changes

- Establish a thin-kernel ownership and promotion contract: upstream libraries own generic mechanics, `agent-core` owns reusable TDT policy/integration, and consumers own domain state and topology.
- Promote a consumer feature into `agent-core` only when it is TDT-specific, is required by at least two active consumers, and is not already a supported upstream contract.
- Accept official Pydantic AI `AgentCapability` and `AgentToolset` values, per-run instructions, and supported overrides through `agent_core.sdk` without re-exporting or cloning upstream concrete types.
- Replace consumer inheritance from `ConsumerConfig` with composition around a stable runtime profile/value object.
- Replace the exhaustive untyped Harness constructor mirror with typed capability passthrough and small TDT-owned policy factories.
- Use `FunctionToolset`/toolsets and `PrepareTools` for tool policy instead of reconstructing agents through private `_function_toolset` state.
- Use official Hooks, Instrumentation, event-stream processing, and deferred-tool continuation without duplicate lifecycle dispatch or private sentinel exceptions.
- Load agent files through `Agent.from_file()`/`Agent.from_spec()` with registered serializable custom capability types while supplying non-serializable live capabilities and toolsets through code composition.
- Adapt TDT persistence to Harness `MemoryStore` and public step stores rather than maintaining a parallel capability implementation.
- Simplify the orchestration facade around native typed LangGraph state, `Command`, interrupts, async execution, and managed checkpointers.
- Consolidate `agent-docs-sync` on one deterministic durable pipeline; keep DynamicWorkflow only as an optional bounded adaptive subflow.
- Migrate `agent-harness` as a second active consumer: inject its gateway explicitly, compose configuration, use official toolsets/capabilities, keep its native consumer-owned `StateGraph`, repair gate routing, and make run/stream/resume use one checkpointer lifecycle.
- Align `agent-harness-stage-modules` so it does not introduce a second tool registry, workflow DSL, runtime-generated TypedDict, string capability catalog, or configuration inheritance hierarchy.
- Record the consumer census: `agent-docs-sync` and `agent-harness` are active external framework consumers; `code-daily-scan` declares `agent-core` but has no source imports; and the `ai-review` deployment bundle contains a packaged `agent-core` copy rather than a distinct source integration.
- Remove legacy dictionary-only capability configuration, redundant workflow/hook adapters, and compatibility shims. All consumers now use the typed SDK composition API.

## Capabilities

### New Capabilities

- `consumer-composition-boundary`: Define ownership, promotion, dependency, and compatibility rules that keep `agent-core` thin.
- `agent-harness-integration`: Define the supported `agent-harness` composition, graph, gate, and persistence contract.

### Modified Capabilities

- `sdk-public-api`: Expose typed official capabilities and toolsets through stable consumer composition APIs.
- `harness-integration`: Replace exhaustive dictionary mirroring with official capability passthrough and narrow policy factories.
- `agent-runtime`: Use supported per-run instructions, toolsets, overrides, streaming, and deferred continuation APIs.
- `hooks`: Make Pydantic AI Hooks the lifecycle authority while preserving TDT hook functions as composable callbacks.
- `agent-yaml-config`: Preserve the full upstream `AgentSpec` and custom capability loading contract.
- `agent-core-memory-lifecycle`: Integrate TDT memory backends through the official Harness memory/store interface.
- `typed-orchestration-state`: Make typed state and reducers the default supported workflow contract.
- `orchestration-command-api`: Prefer native LangGraph `Command` and interrupt/resume semantics over parallel wrapper types.
- `dynamic-workflow`: Limit DynamicWorkflow to bounded adaptive work and configure its full upstream resource/usage contract.
- `agent-docs-sync`: Consolidate duplicate builders and pipelines on the supported framework composition surface.

## Impact

- **Repositories**: primary changes in `agent-core`, `agent-docs-sync`, and `agent-harness`; `code-daily-scan` requires dependency cleanup or a documented packaging reason, and deployed `agent-core` copies require rebuild verification.
- **Dependencies**: no new framework family is expected. Any new Harness extras or version changes require team review before implementation.
- **Public APIs**: adds a typed composition path as the only supported API. Legacy `harness_config`-only configuration and redundant wrappers have been removed.
- **GitNexus blast radius**: `BaseAgent.run` is **CRITICAL** (10 indexed impacted symbols and five processes), `build_full_engine` is **CRITICAL** (eight symbols across all five docs-sync CLI flows), and `agent_harness.workflow.build_graph` is **HIGH** (five symbols across run/stream/resume). Lower-risk composition helpers still require cross-repository contract tests because repository-local indexes under-report cross-repo use.
- **Graphify relationships**: `BaseAgent` directly uses both `AgentRuntime` and `HookAdapter`; `build_full_engine` is called directly by `run_full_dag`; `build_dynamic_orchestrator` is called directly by `run_dynamic_discovery`. These are the migration seams.
- **Dependent work**: `agent-harness-stage-modules` SHALL depend on the converged contract and remain a consumer refactor rather than a source of new framework abstractions.
- **Mobile apps**: no direct iOS or Android runtime change.

## Non-goals

- Enabling every upstream capability by default.
- Removing TDT-owned gateway/auth, budget, skills, tool metadata, audit policy, or domain tools.
- Rewriting external CLI agents in `ai-review` or `jira-epic-report` as Pydantic agents.
- Combining LangGraph, DBOS, and Harness step persistence into one undifferentiated durability mechanism.
- Generalizing a stage-module protocol, tool registry, graph composer, or state-merging DSL in `agent-core` before two consumers demonstrate the same stable need.
