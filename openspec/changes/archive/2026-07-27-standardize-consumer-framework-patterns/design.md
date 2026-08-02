## Context

The `agent-core` SDK provides framework primitives (`BaseAgent`, `BaseTool`, `WorkflowBuilder`, `HookRegistry`, `ConsumerConfig`, `Memory`) and convenience helpers (`build_agent`, `build_toolkit`, `create_consumer_memory`, `register_pack`). The `agent-docs-sync` consumer is the first production consumer of this SDK.

Current state from GitNexus analysis:
- `build_agent` has **zero consumers** — all 3 agent builders in docs-sync manually construct `BaseAgent`
- `build_toolkit` has **zero consumers** — all tool registration is manual
- `register_pack` is used in `agent.py` (5 packs) but **not used** in `agents/generation.py` or `agents/discovery.py`
- 5 pipeline implementations exist; only `full_dag.py` uses `WorkflowEngine`

The `build_toolkit` function has a confirmed bug: it creates a `HookRegistry`, populates it, then discards it without attaching to the returned `ToolRegistry`.

## Goals / Non-Goals

**Goals:**
- Fix `build_toolkit` bug so hook registrations are preserved
- Extend `build_agent` to accept optional `hooks` and `harness_config` params
- Establish minimum hook tier (otel_metrics + structured_audit) for all consumer agents
- Consolidate docs-sync pipelines to single `WorkflowEngine`-based implementation
- Document DynamicWorkflow as optional advanced pattern (stays in pydantic-ai-harness)

**Non-Goals:**
- Absorbing DynamicWorkflow into agent-core (it's a pydantic-ai-harness capability)
- Changing `BaseAgent` constructor (already accepts `hooks` and `harness_config`)
- Changing `ConsumerConfig` (already works correctly)
- Changing tool implementations (all 15 tools already follow `BaseTool[T]`)
- Modifying other consumers (jira-skill, code-daily-scan don't use agent-core SDK yet)

## Decisions

### Decision 1: Fix `build_toolkit` by attaching hooks to registry

**Current bug** (`agent-core/sdk/tools.py`):
```python
def build_toolkit(tools, hooks=None):
    registry = ToolRegistry(include_builtins=False)
    for tool in tools:
        registry.register(tool)
    if hooks:
        hook_registry = HookRegistry()  # created
        for hook_def in hooks:
            hook_registry.register(...)  # populated
    return registry  # hook_registry discarded!
```

**Fix:** Store the `HookRegistry` on the `ToolRegistry` instance and expose it via a property. `ToolRegistry` already has no `hooks` attribute — add one:

```python
def build_toolkit(tools, hooks=None):
    registry = ToolRegistry(include_builtins=False)
    for tool in tools:
        registry.register(tool)
    if hooks:
        hook_registry = HookRegistry()
        for hook_def in hooks:
            point = HookPoint(hook_def["point"])
            hook_registry.register(
                point=point,
                phase=hook_def.get("phase", "before"),
                fn=hook_def["fn"],
                tool_filter=hook_def.get("tool_filter"),
            )
        registry.hooks = hook_registry  # attach!
    return registry
```

**Alternative considered:** Return a tuple `(registry, hooks)` — rejected because it breaks the existing API contract where `build_toolkit` returns a single `ToolRegistry`.

### Decision 2: Extend `build_agent` with optional hooks and harness_config

**Current signature** (`agent-core/sdk/agents.py`):
```python
def build_agent(config, gateway, tools=None, name=None, instructions="", memory=None) -> BaseAgent
```

**New signature:**
```python
def build_agent(
    config: ConsumerConfig,
    gateway: LLMGateway,
    tools: list[Any] | None = None,
    name: str | None = None,
    instructions: str = "",
    memory: Any = None,
    hooks: HookRegistry | None = None,        # NEW
    harness_config: dict[str, Any] | None = None,  # NEW
) -> BaseAgent
```

**Implementation:** Pass `hooks` and `harness_config` through to `BaseAgent` constructor (which already accepts both). Also auto-register standard hook packs if `hooks` is provided but empty:

```python
if hooks is not None and not hooks._hooks:
    register_pack(hooks, "otel_metrics")
    register_pack(hooks, "structured_audit")
```

**Rationale:** `BaseAgent.__init__` already accepts `hooks` and `harness_config`. The SDK helper just needs to pass them through. Auto-registerting standard packs ensures minimum observability.

**Alternative considered:** Create a separate `build_advanced_agent` helper — rejected because it fragments the API. One function with optional params is simpler.

### Decision 3: Standardize hook tiers for consumers

**Tier 0 (always required):** `otel_metrics`, `structured_audit`
- Provides minimum observability for any agent
- Zero-config — works without external services

**Tier 1 (opt-in):** `cost_tracker`, `langfuse_hooks`, `mlflow_hooks`
- Requires configuration (API keys, endpoints)
- Consumer chooses which to enable

**Tier 2 (domain):** Consumer-specific hooks (e.g., `validate_write_path`, `audit_doc_writes`)
- Registered by consumer code, not framework

**Implementation:** `build_agent` auto-registers Tier 0 if `hooks` is provided. Tier 1+ is consumer's responsibility.

### Decision 4: Consolidate pipelines to WorkflowEngine

**Keep:** `full_dag.py` — uses `WorkflowEngine` with conditional routing, checkpointer support, clean handler functions.

**Deprecate (mark with `_deprecated` suffix or delete):**
- `full_pipeline.py` — plain async functions, no DAG
- `sync_pipeline.py` — older WorkflowBuilder DAG, redundant
- `discovery_pipeline.py` — subset of full_dag

**Keep but document as optional:** `dynamic_pipeline.py` — uses pydantic-ai-harness `DynamicWorkflow`, alternative for advanced orchestration

**Migration:** Update `cli.py` entry points to use `full_dag.py` functions. Add deprecation warnings to old entry points.

### Decision 5: DynamicWorkflow stays in pydantic-ai-harness

DynamicWorkflow is a pydantic-ai-harness capability that requires the Monty sandbox. It provides LLM-driven orchestration where the model writes Python to compose sub-agents. This is fundamentally different from agent-core's static `WorkflowEngine`.

**Why not absorb into agent-core:**
- Adds `pydantic-monty` as a dependency (sandboxed code execution)
- Two execution models to maintain (static DAG vs LLM-driven)
- DynamicWorkflow is already well-maintained by pydantic team (v0.7.1, 674 stars)
- agent-core's `WorkflowEngine` covers 90% of use cases without LLM cost

**Documentation:** Add a section to agent-docs-sync README explaining when to use DynamicWorkflow vs WorkflowEngine.

## Risks / Trade-offs

- **[Risk] `build_toolkit` hook attachment breaks existing code** → Mitigation: No existing consumers use `build_toolkit`, so no breakage. The `hooks` attribute is new.
- **[Risk] Auto-registerting Tier 0 hooks adds overhead** → Mitigation: `otel_metrics` and `structured_audit` are lightweight (in-memory counters + structlog). No external service required.
- **[Risk] Pipeline consolidation breaks CLI entry points** → Mitigation: Update CLI to use new functions, keep old functions with deprecation warnings for 1 release.
- **[Trade-off] Single `build_agent` vs multiple helpers** → Chose single function with optional params for API simplicity. Consumers who need complex setup can still construct `BaseAgent` directly.
