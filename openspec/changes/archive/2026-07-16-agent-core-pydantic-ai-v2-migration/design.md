# agent-core pydantic-ai v2.9 Migration — Design

This file mirrors the design spec at `tdt-meta/docs/superpowers/specs/2026-07-13-agent-core-pydantic-ai-v2-migration.md`. The doc there is the durable artifact; this mirror keeps OpenSpec self-contained.

## Guiding constraints

### Composition over inheritance

Every internal component is a **plain class** (not a subclass) that holds a pydantic-ai primitive as a private attribute. No `class MyAgent(pydantic_ai.Agent)`.

```python
# CORRECT — composition
class AgentRuntime:
    _agent: pydantic_ai.Agent
    async def run(self, user_content: str, deps: Any) -> AgentResult:
        result = await self._agent.run(user_content, deps=deps)
        return self._to_result(result)

# FORBIDDEN — inheritance (vendor lock-in)
class MyAgent(pydantic_ai.Agent):  # NOT ALLOWED
    ...
```

### No vendor lock-in

- `pydantic_ai` imports are allowed **only** inside `src/agent_core/_ai/` (new internal package).
- A `TYPE_CHECKING` guard wraps all pydantic-ai imports; production code never imports from `_ai` at runtime.
- `AgentRuntime` exposes a pydantic-ai-agnostic interface.
- An abstract `ModelBackend` protocol defines the LLM model interface so Bifrost, LiteLLM, or direct providers are interchangeable.

## Architecture

```
consumer repos / CLI / examples
        │  (unchanged — same AgentRequest, AgentResult, Flavor, HookRegistry API)
        ▼
┌─────────────────────────────────────────────────────────┐
│  agent-core PUBLIC API  (frozen contract)                │
│  BaseAgent  |  Flavor  |  HookRegistry  |  LLMGateway   │
│  AgentRequest  |  AgentResult  |  SkillSystem           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  INTERNAL LAYER  (pydantic-ai v2.9 only lives here)     │
│                                                         │
│  _ai/                                                    │
│    models.py     — pydantic-ai model init (Bifrost/      │
│                    LiteLLM/OpenAI)                       │
│    agent.py      — AgentRuntime (composes Agent)         │
│    tools.py      — 7 builtin tools as @agent.tool()      │
│    hooks.py      — HookAdapter (facade → pydantic-ai)   │
│    deps.py       — AgentRuntimeDeps dataclass            │
│    types.py      — Internal type aliases                 │
└─────────────────────────────────────────────────────────┘
```

## Layer-by-layer design

### TC002 enforcement

Configuration lives in `pyproject.toml` under `[tool.ruff.lint.per-file-ignores]`. No separate `ruff.toml` exists.

```toml
[tool.ruff.lint.per-file-ignores]
"src/agent_core/_ai/*" = ["TC002"]
```

Note: TC002 is a standard ruff rule; no `[tool.ruff.lint.rules]` addition needed.

### `_ai/models.py` — Model adapter

Factory functions that produce `pydantic_ai.models` model instances. Returns `OpenAIChatModel` (via LiteLLMProvider) for Bifrost, `OpenAIChatModel` (via LiteLLMProvider) for LiteLLM, or direct provider models.

Key design constraint: **`get_model()` returns a model, NOT an Agent**. Agents are constructed only in `BaseAgent.__init__()`.

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.litellm import LiteLLMProvider

def create_bifrost_model(
    *, base_url: str, api_key: str, model: str
) -> OpenAIChatModel:
    """Create an OpenAIChatModel pointing at a Bifrost endpoint."""
    return OpenAIChatModel(
        model,
        provider=LiteLLMProvider(api_base=base_url, api_key=api_key),
    )

def create_litellm_model(
    *, base_url: str, api_key: str = "", model: str
) -> OpenAIChatModel:
    return OpenAIChatModel(
        model,
        provider=LiteLLMProvider(api_base=base_url, api_key=api_key),
    )

def create_model_from_env() -> OpenAIChatModel:
    """Mirror current env-reading behavior used by examples/minimal_agent.py."""
    ...
```

### `_ai/agent.py` — AgentRuntime

The core composition wrapper. Holds a `pydantic_ai.Agent` instance. **Tools are registered at construction time** (decorator or list) and the **tool allowlist is enforced per-call** via `AgentRuntimeDeps.allowed_tools`.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentRuntimeDeps:
    allowed_tools: list[str] | None = None
    correlation_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

class AgentRuntime:
    def __init__(
        self,
        model: Model,
        tools: list[Callable[..., Any]],
        instructions: str = "",
        max_iterations: int = 10,
        timeout_seconds: float = 120.0,
    ) -> None:
        # Tools registered at construction — no per-call tool changes
        self._agent = pydantic_ai.Agent(
            model,
            tools=tools,           # list of @agent.tool() decorated functions
            instructions=instructions,
        )
        self._max_iterations = max_iterations
        self._timeout_seconds = timeout_seconds

    async def run(self, user_content: str, deps: AgentRuntimeDeps) -> AgentResult:
        result = await self._agent.run(
            user_content,
            deps=deps,
            usage_limits=UsageLimits(request_limit=self._max_iterations),
        )
        return self._to_result(result)

    def restrict_tools(self, allow: list[str], deny: list[str]) -> None:
        # For pydantic-ai v2, this requires agent re-construction.
        # Since tools are registered at construction time, this method
        # re-constructs _agent with the filtered tool list.
        ...

    def append_instructions(self, extra: str) -> None:
        self._agent.instructions += f"\n\n{extra}"
```

### `_ai/tools.py` — 7 builtin tool implementations

Seven tools re-implemented as `@Agent[AgentRuntimeDeps].tool()` decorated async functions. Each receives `RunContext[AgentRuntimeDeps]` and returns `str`. Tool allowlist is enforced at runtime via `deps.allowed_tools`.

```python
from pydantic_ai import Agent, RunContext

from agent_core._ai.deps import AgentRuntimeDeps

@Agent[AgentRuntimeDeps].tool()
async def read_file(ctx: RunContext[AgentRuntimeDeps], path: str) -> str:
    """Read the contents of a file at the given path."""
    # Runtime allowlist check
    if ctx.deps.allowed_tools is not None:
        if "read_file" not in ctx.deps.allowed_tools:
            return "Tool 'read_file' is not available for this run."
    ...
```

Tool aliases handled by registering the same function under multiple names in the `Agent` constructor's `tools` list (passing the same function twice with different names).

### `_ai/hooks.py` — HookAdapter

pydantic-ai v2 uses decorator-based hook registration (`@hooks.on.before_model_request`). Our `HookRegistry` uses `register(point, phase, fn)`. The `HookAdapter` bridges by creating a **single pydantic-ai `Hooks` capability** that wraps all our registered hooks, then delegates to our `HookRegistry` facade inside each hook:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks

class HookAdapter:
    def __init__(self, facade: HookRegistry) -> None:
        self._facade = facade
        # All pydantic-ai hooks funnel through our facade
        self._hooks = Hooks()
        self._setup_hooks()

    def _setup_hooks(self) -> None:
        @self._hooks.on.before_run
        async def before_run(ctx: RunContext, request_context):
            return await self._facade.fire_before(HookPoint.RUN, {...})

        @self._hooks.on.after_run
        async def after_run(ctx: RunContext, result):
            return await self._facade.fire_after(HookPoint.RUN, {...}, result)

        @self._hooks.on.before_model_request
        async def before_model_request(ctx, request_context):
            return await self._facade.fire_before(HookPoint.MODEL_REQUEST, {...})

        @self._hooks.on.after_model_request
        async def after_model_request(ctx, request_context, response):
            return await self._facade.fire_after(HookPoint.MODEL_REQUEST, {...}, response)

        @self._hooks.on.before_tool_execute
        async def before_tool_execute(ctx, *, call, tool_def, args):
            return await self._facade.fire_before(HookPoint.TOOL_EXECUTE, {...})

        @self._hooks.on.after_tool_execute
        async def after_tool_execute(ctx, *, call, tool_def, args, result):
            return await self._facade.fire_after(HookPoint.TOOL_EXECUTE, {...}, result)

    def get_capabilities(self) -> list[Hooks]:
        return [self._hooks]
```

The `HookAdapter` is constructed **before** `AgentRuntime` (so hooks are ready before agent construction). The `get_capabilities()` method returns the list passed to `pydantic_ai.Agent(capabilities=[...])`.

### Approval gate — pydantic-ai v2 native

Use `@agent.tool(requires_approval=True)` — pydantic-ai v2 has this built-in. No `AbstractCapability` or deferred-tools needed for the common case. The existing `approval_gate()` function in `agent_base/hooks/builtins.py` is re-implemented to use this native approach:

```python
# Old (hook-based): approval_gate() registered a HookRegistry BEFORE hook
# New (native): shell_execute is registered with requires_approval=True
@Agent[AgentRuntimeDeps].tool(requires_approval=True)
async def shell_execute(ctx: RunContext[AgentRuntimeDeps], command: str) -> str:
    ...
```

`ApprovalGateState` stays. `approval_gate()` stays in `agent_base/hooks/builtins.py` but its implementation changes.

### `llm_gateway/gateway.py` changes

**Key architectural correction:** `BifrostGateway` and `LiteLLMGateway` return **models**, not Agents. They do NOT construct `pydantic_ai.Agent`. They expose `get_model()` for `BaseAgent.__init__()` to use.

```python
class BifrostGateway(LLMGateway):
    def __init__(self, *, base_url, api_key, ...):
        self._model = create_bifrost_model(
            base_url=base_url, api_key=api_key, model="..."
        )
        self._client = httpx.AsyncClient(...)

    def get_model(self) -> OpenAIChatModel:
        """Expose model for BaseAgent to use in AgentRuntime construction."""
        return self._model

    async def complete(self, messages, *, model, tools, ...):
        # Raw single-step LLM call — tools param IGNORED (tools registered on Agent, not here)
        body = {"model": model, "messages": messages}
        resp = await self._client.post("/v1/chat/completions", json=body)
        return _parse_response(resp.json(), model)

    def stream(self, messages, *, model, tools, ...):
        # Raw streaming LLM call
        ...
```

`LLMGateway.complete()` is now a **raw LLM call** (no ReAct loop, no tool execution). The ReAct loop moved to `BaseAgent` → `AgentRuntime`.

`BudgetTracker` wraps every gateway call unchanged — independent of pydantic-ai.

### `agent_base/agent.py` changes

`BaseAgent` becomes a thin facade over `AgentRuntime`. Execution order is critical:

```python
class BaseAgent:
    def __init__(self, *, gateway, tool_registry, model, instructions,
                 flavors, skills, skill_profile, skill_matcher, hooks,
                 max_iterations, timeout_seconds):
        # 1. Hooks constructed FIRST (needed for HookAdapter)
        self._hooks = hooks or HookRegistry()

        # 2. HookAdapter constructed BEFORE AgentRuntime
        #    (pydantic-ai hooks are registered via decorator, before agent construction)
        self._hooks_adapter = HookAdapter(self._hooks)

        # 3. Model resolved from gateway
        self._model = gateway.get_model()

        # 4. Tools collected from tool_registry
        self._tools = _collect_tools(tool_registry)

        # 5. AgentRuntime constructed with model + tools + hooks
        self._runtime = AgentRuntime(
            model=self._model,
            tools=self._tools,
            instructions=self._build_instructions(instructions, flavors, skills),
            max_iterations=max_iterations,
            timeout_seconds=timeout_seconds,
        )

        # 6. Inject pydantic-ai hooks via capabilities
        #    (AgentRuntime._agent was constructed without hooks;
        #     we need to re-construct it with capabilities)
        self._runtime._agent = pydantic_ai.Agent(
            model=self._model,
            tools=self._tools,
            instructions=self._runtime._agent.instructions,
            capabilities=self._hooks_adapter.get_capabilities(),
        )

        # 7. Apply flavors (instructions + tool restrict)
        self._apply_flavors(flavors)
```

The `_react_loop()` method is **deleted**. `BaseAgent.run()` delegates entirely to `AgentRuntime.run()`.

### `tool_registry/` changes

The old `ToolRegistry`, `BaseTool`, `ToolMetadata`, `ToolResult` are removed from the internal implementation path. A `ToolRegistryFacade` in `tool_registry/registry.py` provides read-only access to registered tools for diagnostics/introspection. All 7 built-in tools are removed from `tool_registry/builtins/` and re-implemented in `_ai/tools.py`.

### Flavor mapping

```python
def _apply_flavors(self, flavors: list[Flavor]) -> None:
    merged = merge_flavors(flavors)
    # Instructions
    extra = "\n\n".join(p.content for p in merged.prompts)
    self._runtime.append_instructions(extra)
    # Tool allow/deny — requires agent re-construction
    self._runtime.restrict_tools(
        allow=merged.tool_policy.allow,
        deny=merged.tool_policy.deny,
    )
```

## Migration phases

### Phase 1 — Scaffold & Model Adapter (~4h)
1. Create `src/agent_core/_ai/` package structure
2. Add TC002 to `pyproject.toml` under `[tool.ruff.lint.per-file-ignores]`
3. Implement `_ai/models.py` (Bifrost + LiteLLM model factories, env-based factory)
4. Update BifrostGateway to expose `get_model()` and use `_ai/models.py`
5. Update LiteLLMGateway similarly
6. Verify: gateway tests pass

### Phase 2 — Agent Runtime (~6h)
1. Implement `_ai/agent.py` (`AgentRuntime` + `AgentRuntimeDeps`)
2. Implement `_ai/deps.py`
3. Implement `_ai/types.py`
4. Update `BaseAgent.__init__()` to build `AgentRuntime`
5. Replace `BaseAgent.run()` to delegate to `AgentRuntime.run()`
6. Delete `_react_loop()`, `_build_initial_messages()`, `_build_tool_definitions()`
7. Verify: `examples/minimal_agent.py` runs end-to-end

### Phase 3 — Builtin Tools (~4h)
1. Implement 7 built-in tools in `_ai/tools.py` as `@Agent[AgentRuntimeDeps].tool()`
2. Register tool aliases
3. Create `ToolRegistryFacade` for diagnostics
4. Write unit tests for each tool
5. Delete old `tool_registry/builtins/` directory

### Phase 4 — Hooks (~3h)
1. Implement `_ai/hooks.py` (`HookAdapter`)
2. Re-implement `otel_metrics` via `HookAdapter`
3. Re-implement `structured_audit` via `HookAdapter`
4. Re-implement `approval_gate` using `@agent.tool(requires_approval=True)`
5. Re-implement `cost_tracker` via `HookAdapter`
6. Verify: hook integration tests pass

### Phase 5 — Flavor & Consumer Smoke (~3h)
1. Implement `_apply_flavors()`
2. Verify `examples/flavor_composition.py`
3. Run `ai-review/` test suite (zero changes)
4. Run `code-daily-scan/` test suite (zero changes)

### Phase 6 — Cleanup & Polish (~3h)
1. Remove dead code
2. `ruff check --fix && ruff format && mypy --strict`
3. `pytest` with coverage check
4. CHANGELOG + OpenSpec validate + commit

## Rollback plan

Each phase is independently verifiable.

| Phase | Rollback action |
|-------|---------------|
| Phase 1 | Revert model factory; gateway still works with httpx |
| Phase 2 | Restore `_react_loop()` in `BaseAgent` |
| Phase 3 | Restore `ToolRegistry`/`BaseTool` |
| Phase 4 | Remove `HookAdapter`; `HookRegistry` works standalone |
| Phase 5 | No schema changes; consumer tests catch regressions |
| Phase 6 | Revert commit; no breaking schema changes |

## Key Design Decisions Resolved (Post-Research)

### Decision 1: TC002 placement

`pyproject.toml` under `[tool.ruff.lint.per-file-ignores]`. No separate `ruff.toml`.

### Decision 2: 7 built-in tools (not 6)

`ShellTool` (→ `shell_execute`), `ReadFileTool`, `WriteFileTool`, `GrepSearchTool`, `GitDiffTool`, `HttpRequestTool`, `JsonQueryTool`. All 7 survive.

### Decision 3: Gateway returns MODEL, not Agent

`BifrostGateway` and `LiteLLMGateway` expose `get_model()` returning a `pydantic_ai` model. They do NOT construct `pydantic_ai.Agent`. `AgentRuntime` is constructed in `BaseAgent.__init__()`.

### Decision 4: HookAdapter bridges via single Hooks capability

`HookAdapter` creates one pydantic-ai `Hooks` capability that wraps all our `HookRegistry` hooks. Since pydantic-ai uses decorator registration, `HookAdapter` is constructed **before** `AgentRuntime` and the capabilities are passed to `pydantic_ai.Agent(capabilities=[...])`.

### Decision 5: Approval gate uses `requires_approval=True`

`@agent.tool(requires_approval=True)` is pydantic-ai v2 native. Simpler than `AbstractCapability`. Existing `approval_gate()` function in `agent_base/hooks/builtins.py` is updated to use this.

### Decision 6: BudgetTracker stays unchanged

Independent of pydantic-ai. Tracks USD cost per `budget_id`. `UsageLimits` is per-run and doesn't cover cost.

### Decision 7: `iterations` from `result.usage.requests`

From pydantic-ai `RunResult.usage.requests`. `AgentThought` stays publicly exported but is removed from the internal loop.

### Decision 8: Tool allowlist enforcement

Tools are registered on `Agent` at construction time. The allowlist is enforced **at runtime** inside each `@agent.tool()` function via `ctx.deps.allowed_tools`. No agent re-construction needed per call.

### Decision 9: `BaseAgent.__init__()` execution order

Critical order: (1) `HookRegistry`, (2) `HookAdapter`, (3) `gateway.get_model()`, (4) collect tools from `ToolRegistry` (including consumer-registered custom tools), (5) `AgentRuntime` with model + tools + `output_schema`, (6) re-construct `AgentRuntime._agent` with `capabilities=[hooks_adapter.get_capabilities()]`, (7) apply flavors.

### Decision 10: `output_schema` → pydantic-ai `output_type`

`BaseAgent.run(output_schema=...)` passes through to pydantic-ai `Agent`'s `output_type` parameter. If `output_schema` is a Pydantic model, the result is coerced automatically. `AgentResult.output` retains its `Any` type.

### Decision 11: Custom tool registration (consumer code)

Consumer code calls `ToolRegistry.register(CustomTool())` BEFORE constructing `BaseAgent`. `BaseAgent.__init__()` reads `registry.list_tools()` and collects ALL registered tools — builtins + custom — into a single list passed to `AgentRuntime`. The `ToolRegistry` class itself is NOT modified; only the tool collection step changes.

### Decision 12: `FlavorToolPolicy.require_approval` mapping

`FlavorToolPolicy.require_approval` (a `list[str]`) causes those tools to be registered with `requires_approval=True`. This complements `ApprovalGateState.dangerous_tools` which blocks tools at the hook level.

### Decision 13: `LLMGateway()` no-arg construction

Both examples (`minimal_agent.py`, `custom_tool.py`) call `gateway = LLMGateway()` with no arguments. `LLMGateway` is the abstract base class — this actually raises `TypeError` at runtime today. The migration DOES NOT fix this; the correct usage is `gateway = create_gateway()` or `gateway = BifrostGateway(...)`. This is a pre-existing usage bug in the examples, not introduced by migration.
